"""DB layer: SQLite or MySQL. Tables: users, user_settings."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "app.db"

# Use MySQL if DATABASE_URL or MYSQL_URL (e.g. Railway) or MYSQL_HOST is set
DATABASE_URL = (os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or "").strip()
USE_MYSQL = DATABASE_URL.startswith("mysql") or bool(os.getenv("MYSQL_HOST"))


def _sqlite_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _mysql_connection():
    import pymysql
    # Prefer explicit env vars; else parse DATABASE_URL (mysql://user:password@host:port/dbname)
    host = os.getenv("MYSQL_HOST")
    if host:
        return pymysql.connect(
            host=host,
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "email_sender"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    url = DATABASE_URL.replace("mysql+pymysql://", "").replace("mysql://", "")
    # user:password@host:port/database
    at = url.rfind("@")
    slash = url.find("/", at + 1) if at >= 0 else url.find("/")
    if at >= 0 and slash >= 0:
        user, password = url[:at].split(":", 1) if ":" in url[:at] else (url[:at], "")
        host_port = url[at + 1:slash]
        database = url[slash + 1:].split("?")[0]
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1]) if ":" in host_port else 3306
    else:
        host, user, password, database, port = "localhost", "root", "", "email_sender", 3306
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_connection():
    if USE_MYSQL:
        return _mysql_connection()
    return _sqlite_connection()


def _row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        if USE_MYSQL:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INT PRIMARY KEY,
                    sender_email VARCHAR(255) NOT NULL,
                    app_password_encrypted TEXT NOT NULL,
                    your_name VARCHAR(255) NOT NULL,
                    total_experience VARCHAR(255) NOT NULL,
                    technology VARCHAR(255) NOT NULL,
                    experience_from_date VARCHAR(255) NOT NULL,
                    resume_path TEXT NOT NULL,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    sender_email TEXT NOT NULL,
                    app_password_encrypted TEXT NOT NULL,
                    your_name TEXT NOT NULL,
                    total_experience TEXT NOT NULL,
                    technology TEXT NOT NULL,
                    experience_from_date TEXT NOT NULL,
                    resume_path TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
        cur.close()


def create_user(email: str, password_hash: str) -> int | None:
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s)" if USE_MYSQL else "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email.strip().lower(), password_hash),
            )
            uid = cur.lastrowid
            cur.close()
            return uid
    except Exception as e:
        if "Duplicate" in str(e) or "UNIQUE" in str(e) or "1062" in str(e):
            return None
        raise


def get_user_by_email(email: str) -> dict | None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = %s" if USE_MYSQL else "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
            (email.strip().lower(),),
        )
        row = cur.fetchone()
        cur.close()
        return _row_to_dict(row)


def get_user_settings(user_id: int) -> dict | None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path FROM user_settings WHERE user_id = %s" if USE_MYSQL else "SELECT sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path FROM user_settings WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()
        return _row_to_dict(row)


def save_user_settings(
    user_id: int,
    sender_email: str,
    app_password_encrypted: str,
    your_name: str,
    total_experience: str,
    technology: str,
    experience_from_date: str,
    resume_path: str,
) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        if USE_MYSQL:
            cur.execute("""
                INSERT INTO user_settings (user_id, sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sender_email = VALUES(sender_email),
                    app_password_encrypted = VALUES(app_password_encrypted),
                    your_name = VALUES(your_name),
                    total_experience = VALUES(total_experience),
                    technology = VALUES(technology),
                    experience_from_date = VALUES(experience_from_date),
                    resume_path = VALUES(resume_path),
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path))
        else:
            cur.execute("""
                INSERT INTO user_settings (user_id, sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    sender_email = excluded.sender_email,
                    app_password_encrypted = excluded.app_password_encrypted,
                    your_name = excluded.your_name,
                    total_experience = excluded.total_experience,
                    technology = excluded.technology,
                    experience_from_date = excluded.experience_from_date,
                    resume_path = excluded.resume_path,
                    updated_at = datetime('now')
            """, (user_id, sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path))
        cur.close()
