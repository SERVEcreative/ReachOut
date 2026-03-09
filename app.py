"""ReachOut – run: python app.py"""
import config
config.load_env()

from datetime import timedelta
from flask import Flask
from db import init_db
from routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.secret_key = config.get_secret_key()

    if config.is_production():
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    init_db()
    register_blueprints(app)

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    return app


app = create_app()


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
