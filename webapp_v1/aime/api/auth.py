from __future__ import annotations

from datetime import datetime, timedelta, UTC

from flask import Blueprint, current_app, g, jsonify, request, session

from ..extensions import db
from ..models import PasswordResetToken, User, UserPreference
from ..security import (
    auth_required,
    current_user,
    hash_password,
    issue_session,
    rate_limit,
    revoke_current_session,
    validate_email,
    validate_password,
    verify_password,
)
from .common import iso


bp = Blueprint("auth_api", __name__)


def _utcnow_naive():
    return datetime.now(UTC).replace(tzinfo=None)


def user_payload(user: User):
    pref = user.preferences
    return {
        "id": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "accountStatus": user.account_status,
        "createdAt": iso(user.created_at),
        "updatedAt": iso(user.updated_at),
        "preferences": {
            "theme": pref.theme if pref else "dark",
            "notificationsEnabled": pref.notifications_enabled if pref else True,
            "privacyLevel": pref.privacy_level if pref else "standard",
            "autoSaveAnalysis": pref.auto_save_analysis if pref else False,
            "retentionDays": pref.retention_days if pref else 90,
        },
    }


@bp.post("/auth/register")
@rate_limit(limit=8, window_seconds=60)
def register():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("fullName") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if len(full_name) < 2:
        return jsonify({"error": "Full name is required."}), 400
    if not validate_email(email):
        return jsonify({"error": "Invalid email."}), 400
    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"error": msg}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use."}), 409

    user = User(full_name=full_name, email=email, password_hash=hash_password(password), account_status="active")
    db.session.add(user)
    db.session.flush()
    pref = UserPreference(user_id=user.id, auto_save_analysis=current_app.config["AUTO_SAVE_ANALYSIS"])
    db.session.add(pref)
    db.session.commit()
    issue_session(user)
    return jsonify({"success": True, "user": user_payload(user)}), 201


@bp.post("/auth/login")
@rate_limit(limit=10, window_seconds=60)
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    if user.account_status != "active":
        return jsonify({"error": "Account is not active"}), 403

    issue_session(user)
    return jsonify({"success": True, "user": user_payload(user)})


@bp.post("/auth/logout")
def logout():
    revoke_current_session()
    return jsonify({"success": True})


@bp.get("/auth/me")
@auth_required
def me():
    return jsonify({"success": True, "user": user_payload(g.current_user)})


@bp.post("/auth/session/renew")
@auth_required
def renew_session():
    revoke_current_session()
    issue_session(g.current_user)
    return jsonify({"success": True})


@bp.post("/auth/password/change")
@auth_required
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get("currentPassword") or ""
    new_password = data.get("newPassword") or ""

    if not verify_password(g.current_user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 400
    ok, msg = validate_password(new_password)
    if not ok:
        return jsonify({"error": msg}), 400

    g.current_user.password_hash = hash_password(new_password)
    db.session.commit()
    return jsonify({"success": True})


@bp.post("/auth/password/forgot")
@rate_limit(limit=5, window_seconds=300)
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if user:
        token = PasswordResetToken.generate()
        ttl = current_app.config["RESET_TOKEN_TTL_MINUTES"]
        db.session.add(
            PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=_utcnow_naive() + timedelta(minutes=ttl),
            )
        )
        db.session.commit()
    return jsonify({"success": True, "message": "If the email exists, a reset token was issued."})


@bp.post("/auth/password/reset")
@rate_limit(limit=8, window_seconds=300)
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    password = data.get("password") or ""
    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"error": msg}), 400

    row = PasswordResetToken.query.filter_by(token=token).first()
    expires = row.expires_at.replace(tzinfo=None) if row and row.expires_at.tzinfo else (row.expires_at if row else None)
    if not row or row.used_at or expires < _utcnow_naive():
        return jsonify({"error": "Invalid or expired token"}), 400

    user = db.session.get(User, row.user_id)
    user.password_hash = hash_password(password)
    row.used_at = _utcnow_naive()
    db.session.commit()
    return jsonify({"success": True})


@bp.delete("/auth/account")
@auth_required
def delete_account():
    user = g.current_user
    revoke_current_session()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({"success": True})
