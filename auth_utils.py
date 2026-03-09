"""Password hashing and app-password encryption (Fernet)."""
import base64
import hashlib
import os

from werkzeug.security import check_password_hash, generate_password_hash

def _get_fernet_key():
    from cryptography.fernet import Fernet
    secret = os.getenv("SECRET_KEY", "change-me-in-production")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="scrypt")


def check_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def encrypt_app_password(plain: str) -> str:
    if not plain:
        return ""
    f = _get_fernet_key()
    return base64.urlsafe_b64encode(f.encrypt(plain.encode())).decode()


def decrypt_app_password(encrypted: str) -> str:
    if not encrypted:
        return ""
    f = _get_fernet_key()
    return f.decrypt(base64.urlsafe_b64decode(encrypted.encode())).decode()
