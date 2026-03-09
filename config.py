"""Env loading and app config."""
import os
import logging

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(PROJECT_DIR, ".env")
DEFAULT_SECRET = "change-me-in-production-multi-user"


def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass


def is_production():
    """True when running in production (Railway, etc.): PORT set or FLASK_ENV/ENV=production."""
    if os.getenv("FLASK_ENV") == "production" or os.getenv("ENV") == "production":
        return True
    if os.getenv("PORT"):
        return True
    return False


def get_secret_key():
    key = os.getenv("SECRET_KEY", DEFAULT_SECRET)
    if is_production() and (not key or key == DEFAULT_SECRET):
        logging.warning(
            "SECRET_KEY is default or missing in production. Set SECRET_KEY in your environment."
        )
    return key or DEFAULT_SECRET
