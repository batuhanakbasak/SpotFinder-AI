# config.py
import os
from dotenv import load_dotenv

# .env dosyasını (varsa) yükle
load_dotenv()

class Config:
    # Flask için
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

    # PostgreSQL ayarları
    DB_HOST = os.getenv("DB_HOST", "94.55.180.77")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "parking_ai")
    DB_USER = os.getenv("DB_USER", "batuhante")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Gx7!rP92@Klm#4Qs")  # burayı kendi şifrenle değiştir

    MODEL_DIR = os.getenv(
        "MODEL_DIR",
        os.path.join(os.path.dirname(__file__), "models")
    )