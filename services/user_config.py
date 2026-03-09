"""User config and setup form data from DB."""
from db import get_user_settings
from auth_utils import decrypt_app_password


def get_config_for_user(user_id: int) -> dict | None:
    row = get_user_settings(user_id)
    if not row:
        return None
    try:
        app_password = decrypt_app_password(row["app_password_encrypted"])
    except Exception:
        return None
    return {
        "sender_email": row["sender_email"],
        "app_password": app_password,
        "your_name": row["your_name"],
        "resume_path": row["resume_path"] or None,
        "experience": None,
        "custom_message": None,
        "total_experience": row["total_experience"] or None,
        "technology": row["technology"] or None,
        "experience_from_date": row["experience_from_date"] or None,
    }


def get_setup_form_data(user_id: int) -> dict:
    row = get_user_settings(user_id)
    if not row:
        return {}
    return {
        "your_name": row["your_name"] or "",
        "sender_email": row["sender_email"] or "",
        "total_experience": row["total_experience"] or "",
        "technology": row["technology"] or "",
        "experience_from_date": row["experience_from_date"] or "",
        "resume_path": row["resume_path"] or "",
    }
