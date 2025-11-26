# app.py
from flask import Flask
from config import Config
from db import close_db
from ai import load_models
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # modelleri yükle
    load_models(app)

    # DB bağlantısını request sonunda kapat
    app.teardown_appcontext(close_db)

    # blueprint'leri kaydet
    register_blueprints(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
