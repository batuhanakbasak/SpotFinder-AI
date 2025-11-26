# ai.py
import os
import pickle
from datetime import datetime, timedelta
from math import radians, sin, cos, asin, sqrt

import pandas as pd
import numpy as np
from flask import current_app
from db import get_db


# ---- Mesafe hesabı (metre) ----
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * asin(min(1, np.sqrt(a)))
    return R * c


# ---- App başlarken modelleri yükleyen fonksiyon ----
def load_models(app):
    model_dir = app.config["MODEL_DIR"]

    with open(os.path.join(model_dir, "model_occ_ratio.pkl"), "rb") as f:
        app.model_occ_ratio = pickle.load(f)

    with open(os.path.join(model_dir, "model_next_free.pkl"), "rb") as f:
        app.model_next_free = pickle.load(f)

    with open(os.path.join(model_dir, "model_avg_duration.pkl"), "rb") as f:
        app.model_avg_duration = pickle.load(f)


# ---- Tek bir zone için feature + 3 model prediction ----
def get_zone_features_and_predictions(zone_id: int):
    app = current_app
    conn = get_db()
    cur = conn.cursor()

    # zone bilgisi
    cur.execute("""
        SELECT id, code, name, lat, lng, radius_m, capacity
        FROM zones
        WHERE id = %s
    """, (zone_id,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        return None

    zid, code, name, lat, lng, radius_m, capacity = row

    # aktif session sayısı
    cur.execute("""
        SELECT COUNT(*)
        FROM parking_sessions
        WHERE zone_id = %s AND status = 'active'
    """, (zid,))
    current_occupied = cur.fetchone()[0]
    current_free = max(0, capacity - current_occupied)

    # son 1 saatlik event istatistikleri
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    cur.execute("""
        SELECT event_type, COUNT(*)
        FROM spot_events
        WHERE zone_id = %s AND event_time >= %s
        GROUP BY event_type
    """, (zid, one_hour_ago))
    rows = cur.fetchall()
    cur.close()

    past_arrivals = 0
    past_departures = 0
    for etype, cnt in rows:
        if etype == 'became_occupied':
            past_arrivals = cnt
        elif etype == 'became_free':
            past_departures = cnt

    # zaman feature'ları
    hour = now.hour
    day_of_week = now.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0
    weather = "sunny"  # şimdilik sabit

    data = {
        "hour": [hour],
        "day_of_week": [day_of_week],
        "is_weekend": [is_weekend],
        "weather": [weather],
        "zone_id": [code],           # 'Z1', 'Z2'...
        "zone_capacity": [capacity],
        "current_occupied": [current_occupied],
        "current_free": [current_free],
        "past_arrivals": [past_arrivals],
        "past_departures": [past_departures],
    }
    df = pd.DataFrame(data)

    # Model 3: ortalama park süresi
    avg_duration = float(app.model_avg_duration.predict(df)[0])

    # Model 1: 1 saat sonraki doluluk oranı
    occ_next = float(app.model_occ_ratio.predict(df)[0])
    occ_next = float(np.clip(occ_next, 0.0, 1.0))

    # Model 2: ilk boş yer süresi (sadece full ise)
    if current_free > 0:
        wait_time = 0.0
    else:
        df2 = df.copy()
        df2["avg_duration_total"] = [avg_duration]
        wait_time = float(app.model_next_free.predict(df2)[0])
        if wait_time < 0:
            wait_time = 0.0

    return {
        "zone_id": zid,
        "zone_code": code,
        "name": name,
        "lat": lat,
        "lng": lng,
        "radius_m": radius_m,
        "capacity": capacity,
        "current_occupied": current_occupied,
        "current_free": current_free,
        "predictions": {
            "occupancy_next_hour": occ_next,
            "wait_time_minutes": wait_time,
            "avg_duration_minutes": avg_duration,
        },
    }
