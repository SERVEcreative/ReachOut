from flask import Blueprint, render_template, redirect

from db import get_user_settings
from services import get_current_user_id, get_config_for_user, get_setup_form_data

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    user_id = get_current_user_id()
    if not user_id:
        return redirect("/login")
    config = get_config_for_user(user_id)
    if not config:
        return redirect("/setup")
    return render_template("index.html")


@main_bp.route("/setup", methods=["GET"])
def setup():
    user_id = get_current_user_id()
    if not user_id:
        return redirect("/login")
    current = get_setup_form_data(user_id)
    has_settings = get_user_settings(user_id) is not None
    return render_template(
        "setup.html",
        current=current,
        first_time=not has_settings,
    )
