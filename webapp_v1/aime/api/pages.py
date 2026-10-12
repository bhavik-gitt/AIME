from flask import Blueprint, render_template


bp = Blueprint("pages", __name__)


@bp.get("/")
def landing():
    return render_template("landing.html")


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/contact")
def contact():
    return render_template("contact.html")


@bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.get("/terms")
def terms():
    return render_template("terms.html")


@bp.get("/login")
def login_page():
    return render_template("login.html")


@bp.get("/register")
def register_page():
    return render_template("register.html")


@bp.get("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")


@bp.get("/reset-password")
def reset_password_page():
    return render_template("reset_password.html")


@bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@bp.get("/audio")
def audio_page():
    return render_template("audio.html")


@bp.get("/video")
def video_page():
    return render_template("video.html")


@bp.get("/history")
def history_page():
    return render_template("history.html")


@bp.get("/analytics")
def analytics_page():
    return render_template("analytics.html")


@bp.get("/profile")
def profile_page():
    return render_template("profile.html")


@bp.get("/settings")
def settings_page():
    return render_template("settings.html")


@bp.get("/reports")
def reports_page():
    return render_template("reports.html")


@bp.get("/results")
def results_page():
    return render_template("results.html")


@bp.get("/insights")
def insights_page():
    return render_template("insights.html")


@bp.get("/help")
def help_page():
    return render_template("help.html")
