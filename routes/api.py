from flask import Blueprint, request, jsonify

from send_job_inquiry import send_inquiry_to
from db import get_user_settings, save_user_settings
from auth_utils import encrypt_app_password, decrypt_app_password
from services import get_current_user_id, get_config_for_user

api_bp = Blueprint("api", __name__)


@api_bp.route("/setup", methods=["POST"])
def api_setup():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Please log in."}), 401
    data = request.get_json(silent=True) or {}
    sender_email = (data.get("sender_email") or "").strip()
    app_password = (data.get("app_password") or "").strip()
    your_name = (data.get("your_name") or "").strip() or "Candidate"
    total_experience = (data.get("total_experience") or "").strip()
    technology = (data.get("technology") or "").strip()
    experience_from_date = (data.get("experience_from_date") or "").strip()
    resume_path = (data.get("resume_path") or "").strip() or ""

    existing = get_user_settings(user_id)
    if existing and not app_password:
        app_password = decrypt_app_password(existing["app_password_encrypted"])
    else:
        app_password = app_password or ""

    if not sender_email:
        return jsonify({"success": False, "error": "Sender email is required."}), 400
    if not app_password:
        return jsonify({"success": False, "error": "App password is required."}), 400

    try:
        save_user_settings(
            user_id,
            sender_email=sender_email,
            app_password_encrypted=encrypt_app_password(app_password),
            your_name=your_name,
            total_experience=total_experience,
            technology=technology,
            experience_from_date=experience_from_date,
            resume_path=resume_path,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/send", methods=["POST"])
def api_send():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Please log in."}), 401
    config = get_config_for_user(user_id)
    if not config:
        return jsonify({"success": False, "error": "Please complete Setup first."}), 400
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    result = send_inquiry_to(email, config=config)
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 400
