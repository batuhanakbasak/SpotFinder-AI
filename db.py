# db.py
import psycopg2
from flask import g, current_app

def get_db():
    """
    Request süresince kullanılacak tek bir DB bağlantısı döner.
    İlk çağrıda açar, sonrakiler aynı connection'ı kullanır.
    """
    if "db_conn" not in g:
        cfg = current_app.config
        g.db_conn = psycopg2.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            dbname=cfg["DB_NAME"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
        )
    return g.db_conn

def close_db(e=None):
    """
    Request bittikten sonra bağlantıyı kapatır (Flask teardown hook'u çağırır).
    """
    db_conn = g.pop("db_conn", None)

    if db_conn is not None:
        db_conn.close()
