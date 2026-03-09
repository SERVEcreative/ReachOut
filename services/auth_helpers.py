from flask import session


def get_current_user_id():
    return session.get("user_id")
