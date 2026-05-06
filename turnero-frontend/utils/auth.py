from functools import wraps
from flask import flash, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("token"):
            flash("Debe iniciar sesión", "warning")
            return redirect(url_for("auth.login_view"))
        return view(*args, **kwargs)

    return wrapper
