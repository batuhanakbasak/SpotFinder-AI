# routes/health.py
from flask import Blueprint, jsonify
from db import get_db

bp = Blueprint("health", __name__)

@bp.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db_error": str(e)}), 500
