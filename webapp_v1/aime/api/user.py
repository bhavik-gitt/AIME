from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..extensions import db
from ..models import EmotionAnalysis, UserPreference
from ..security import auth_required, validate_email


bp = Blueprint("user_api", __name__)


@bp.get("/users/profile")
@auth_required
def get_profile():
    return jsonify(
        {
            "success": True,
            "profile": {
                "id": g.current_user.id,
                "fullName": g.current_user.full_name,
                "email": g.current_user.email,
                "accountStatus": g.current_user.account_status,
                "createdAt": g.current_user.created_at.isoformat(),
            },
        }
    )


@bp.patch("/users/profile")
@auth_required
def update_profile():
    data = request.get_json(silent=True) or {}
    full_name = data.get("fullName")
    email = data.get("email")

    if full_name is not None:
        full_name = full_name.strip()
        if len(full_name) < 2:
            return jsonify({"error": "Full name must have at least 2 characters"}), 400
        g.current_user.full_name = full_name

    if email is not None:
        email = email.strip().lower()
        if not validate_email(email):
            return jsonify({"error": "Invalid email"}), 400
        exists = type(g.current_user).query.filter(type(g.current_user).email == email, type(g.current_user).id != g.current_user.id).first()
        if exists:
            return jsonify({"error": "Email is already in use"}), 409
        g.current_user.email = email

    db.session.commit()
    return jsonify({"success": True})


@bp.get("/users/preferences")
@auth_required
def get_preferences():
    pref = UserPreference.query.filter_by(user_id=g.current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=g.current_user.id)
        db.session.add(pref)
        db.session.commit()

    return jsonify(
        {
            "success": True,
            "preferences": {
                "theme": pref.theme,
                "notificationsEnabled": pref.notifications_enabled,
                "privacyLevel": pref.privacy_level,
                "autoSaveAnalysis": pref.auto_save_analysis,
                "retentionDays": pref.retention_days,
            },
        }
    )


@bp.patch("/users/preferences")
@auth_required
def update_preferences():
    data = request.get_json(silent=True) or {}
    pref = UserPreference.query.filter_by(user_id=g.current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=g.current_user.id)
        db.session.add(pref)

    if "theme" in data:
        if data["theme"] not in {"dark", "light"}:
            return jsonify({"error": "Invalid theme"}), 400
        pref.theme = data["theme"]
    if "notificationsEnabled" in data:
        pref.notifications_enabled = bool(data["notificationsEnabled"])
    if "privacyLevel" in data:
        pref.privacy_level = str(data["privacyLevel"])
    if "autoSaveAnalysis" in data:
        pref.auto_save_analysis = bool(data["autoSaveAnalysis"])
    if "retentionDays" in data:
        retention = int(data["retentionDays"])
        if retention < 1 or retention > 3650:
            return jsonify({"error": "retentionDays must be between 1 and 3650"}), 400
        pref.retention_days = retention

    db.session.commit()
    return jsonify({"success": True})


@bp.get("/users/export")
@auth_required
def export_user_data():
    analyses = EmotionAnalysis.query.filter_by(user_id=g.current_user.id).all()
    return jsonify(
        {
            "success": True,
            "user": {
                "id": g.current_user.id,
                "fullName": g.current_user.full_name,
                "email": g.current_user.email,
                "createdAt": g.current_user.created_at.isoformat(),
            },
            "analysisCount": len(analyses),
        }
    )
