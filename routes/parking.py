# routes/parking.py
import secrets
from flask import Blueprint, jsonify, request
from db import get_db
from ai import haversine_m

bp = Blueprint("parking", __name__)

@bp.route("/parking/start", methods=["POST"])
def parking_start():
    data = request.get_json(force=True, silent=True) or {}

    qr_code = data.get("qr_code")
    lat = data.get("lat")
    lng = data.get("lng")
    vehicle_plate = data.get("vehicle_plate")
    plate_country = data.get("plate_country")

    if not vehicle_plate:
        return jsonify({"error": "vehicle_plate required"}), 400

    conn = get_db()
    cur = conn.cursor()

    zone_id = None
    zone_code = None
    qr_id = None

    # a) QR varsa qrs üzerinden zone bul
    if qr_code:
        cur.execute("""
            SELECT q.id, q.zone_id, z.code, z.lat, z.lng, z.radius_m
            FROM qrs q
            JOIN zones z ON z.id = q.zone_id
            WHERE q.code_value = %s
        """, (qr_code,))
        row = cur.fetchone()
        if row is None:
            cur.close()
            return jsonify({"error": "invalid qr_code"}), 400
        qr_id, zone_id, zone_code, zlat, zlng, radius_m = row

    # b) GPS varsa ve zone henüz belirlenmediyse, en yakın zone'u bul
    if lat is not None and lng is not None and zone_id is None:
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except ValueError:
            cur.close()
            return jsonify({"error": "lat/lng must be numbers"}), 400

        cur.execute("SELECT id, code, lat, lng, radius_m FROM zones;")
        zones = cur.fetchall()
        if not zones:
            cur.close()
            return jsonify({"error": "no zones defined"}), 500

        best = None
        best_dist = None
        for zid, code, zlat, zlng, radius_m in zones:
            d = haversine_m(lat_f, lng_f, zlat, zlng)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (zid, code)

        zone_id, zone_code = best

    if zone_id is None:
        cur.close()
        return jsonify({"error": "either qr_code or lat/lng required"}), 400

    # 🔐 Güçlü random session_token üret
    session_token = secrets.token_hex(32)  # 64 karakter

    # parking_session oluştur
    cur.execute("""
        INSERT INTO parking_sessions (zone_id, qr_id, vehicle_plate, plate_country, status, started_at, session_token)
        VALUES (%s, %s, %s, %s, 'active', NOW(), %s)
        RETURNING id, started_at;
    """, (zone_id, qr_id, vehicle_plate, plate_country, session_token))
    session_id, started_at = cur.fetchone()

    # became_occupied event
    cur.execute("""
        INSERT INTO spot_events (zone_id, session_id, event_type, event_time)
        VALUES (%s, %s, 'became_occupied', NOW());
    """, (zone_id, session_id))

    conn.commit()
    cur.close()

    return jsonify({
        "session_id": session_id,
        "session_token": session_token,   # 🔐 BURADA FRONTEND'E DÖNÜYORUZ
        "zone_id": zone_id,
        "zone_code": zone_code,
        "vehicle_plate": vehicle_plate,
        "plate_country": plate_country,
        "started_at": started_at.isoformat()
    })


@bp.route("/parking/end", methods=["POST"])
def parking_end():
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("session_id")
    session_token = data.get("session_token")

    if not session_id or not session_token:
        return jsonify({"error": "session_id and session_token required"}), 400

    conn = get_db()
    cur = conn.cursor()

    # Hem ID hem token ile eşleşmeyi zorunlu kılıyoruz
    cur.execute("""
        SELECT zone_id, status
        FROM parking_sessions
        WHERE id = %s AND session_token = %s;
    """, (session_id, session_token))
    row = cur.fetchone()

    if row is None:
        cur.close()
        # Yanlış ID/token kombinasyonu → yetkisiz
        return jsonify({"error": "unauthorized or session not found"}), 403

    zone_id, status = row
    if status != 'active':
        cur.close()
        return jsonify({"error": "session not active"}), 400

    # session'ı bitir
    cur.execute("""
        UPDATE parking_sessions
        SET status = 'ended', ended_at = NOW()
        WHERE id = %s;
    """, (session_id,))

    # became_free event
    cur.execute("""
        INSERT INTO spot_events (zone_id, session_id, event_type, event_time)
        VALUES (%s, %s, 'became_free', NOW());
    """, (zone_id, session_id))

    conn.commit()
    cur.close()

    return jsonify({"ok": True})
