# routes/__init__.py
from .health import bp as health_bp
from .zones import bp as zones_bp
from .parking import bp as parking_bp

def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(zones_bp,  url_prefix="/api")
    app.register_blueprint(parking_bp, url_prefix="/api")
