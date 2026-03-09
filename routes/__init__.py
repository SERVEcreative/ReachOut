from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
