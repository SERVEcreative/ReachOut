from flask import Blueprint, render_template, request, redirect, session

from db import create_user, get_user_by_email
from auth_utils import hash_password, check_password
from services import get_current_user_id

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if get_current_user_id():
            return redirect("/")
        return render_template("register.html", email="")
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    if not email or "@" not in email:
        return render_template("register.html", error="Valid email required", email=email)
    if not password or len(password) < 6:
        return render_template("register.html", error="Password must be at least 6 characters", email=email)
    if get_user_by_email(email):
        return render_template(
            "register.html",
            error="Email already registered. Use Log in or try another email.",
            email=email,
        )
    user_id = create_user(email, hash_password(password))
    if not user_id:
        return render_template("register.html", error="Registration failed. Try again.", email=email)
    session.permanent = True
    session["user_id"] = user_id
    return redirect("/")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if get_current_user_id():
            return redirect("/")
        msg = request.args.get("msg")
        error = "Your session expired. Please log in again." if msg == "session_expired" else None
        return render_template("login.html", error=error)
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    user = get_user_by_email(email)
    if not user or not check_password(user["password_hash"], password):
        return (
            render_template(
                "login.html",
                error="Invalid email or password. Use Test@123 if you ran seed_test_user.py.",
            ),
            401,
        )
    session.permanent = True
    session["user_id"] = user["id"]
    return redirect("/")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")
