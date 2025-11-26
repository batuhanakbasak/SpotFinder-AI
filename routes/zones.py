# routes/zones.py
from flask import Blueprint, jsonify, request
from db import get_db
from ai import haversine_m, get_zone_features_and_predictions

bp = Blueprint("zones", __name__)

# 3.3 GET /api/zones
@bp.route("/zones", methods=["GET"])
def list_zones():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, code, name, lat, lng, radius_m, capacity
        FROM zones
        ORDER BY id;
    """)
    rows = cur.fetchall()
    cur.close()

    zones = []
    for r in rows:
        zones.append({
            "id": r[0],
            "code": r[1],
            "name": r[2],
            "lat": r[3],
            "lng": r[4],
            "radius_m": r[5],
            "capacity": r[6],
        })
    return jsonify(zones)


# 3.4 GET /api/zones/nearest?lat=..&lng=..
@bp.route("/zones/nearest", methods=["GET"])
def nearest_zone():
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng query params required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, code, lat, lng, radius_m FROM zones;")
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return jsonify({"error": "no zones defined"}), 500

    best = None
    best_dist = None
    for zid, code, zlat, zlng, radius_m in rows:
        d = haversine_m(lat, lng, zlat, zlng)
        if best_dist is None or d < best_dist:
            best_dist = d
            best = (zid, code, radius_m)

    zid, code, radius_m = best
    return jsonify({
        "zone_id": zid,
        "zone_code": code,
        "distance_m": best_dist,
        "radius_m": radius_m,
        "inside": best_dist <= radius_m
    })


# 3.5 GET /api/zones/status
@bp.route("/zones/status", methods=["GET"])
def zones_status():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM zones ORDER BY id;")
    zone_ids = [r[0] for r in cur.fetchall()]
    cur.close()

    result = []
    for zid in zone_ids:
        info = get_zone_features_and_predictions(zid)
        if info:
            result.append({
                "zone_id": info["zone_id"],
                "zone_code": info["zone_code"],
                "name": info["name"],
                "lat": info["lat"],
                "lng": info["lng"],
                "radius_m": info["radius_m"],
                "capacity": info["capacity"],
                "current_occupied": info["current_occupied"],
                "current_free": info["current_free"],
                "pred": info["predictions"],
            })

    return jsonify(result)


# 3.6 GET /api/zones/<id>/status
@bp.route("/zones/<int:zone_id>/status", methods=["GET"])
def zone_status(zone_id):
    info = get_zone_features_and_predictions(zone_id)
    if not info:
        return jsonify({"error": "zone not found"}), 404

    return jsonify({
        "zone_id": info["zone_id"],
        "zone_code": info["zone_code"],
        "name": info["name"],
        "lat": info["lat"],
        "lng": info["lng"],
        "radius_m": info["radius_m"],
        "capacity": info["capacity"],
        "current_occupied": info["current_occupied"],
        "current_free": info["current_free"],
        "pred": info["predictions"],
    })
