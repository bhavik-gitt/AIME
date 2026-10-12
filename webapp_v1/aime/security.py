from __future__ import annotations

import hashlib
import hmac
import re
from datetime import datetime, UTC
from functools import wraps
from typing import Callable

from argon2 import PasswordHasher
from flask import current_app, g, jsonify, request, session

from .extensions import db
from .models import AuthSession, User


_password_hasher = PasswordHasher()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(stored_hash, password)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password or "") < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include a lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include a number."
    return True, ""


def hash_session_token(token: str) -> str:
    secret = current_app.config["SECRET_KEY"].encode("utf-8")
    digest = hmac.new(secret, token.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def issue_session(user: User, hours: int = 24) -> str:
    import secrets

    token = secrets.token_urlsafe(48)
    token_hash = hash_session_token(token)
    row = AuthSession(
        user_id=user.id,
        session_token_hash=token_hash,
        expires_at=AuthSession.new_expiry(hours=hours),
    )
    db.session.add(row)
    db.session.commit()
    session["session_token"] = token
    return token


def _utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def revoke_current_session() -> None:
    raw = session.get("session_token")
    if not raw:
        return
    token_hash = hash_session_token(raw)
    row = AuthSession.query.filter_by(session_token_hash=token_hash).first()
    if row and not row.revoked_at:
        row.revoked_at = _utcnow_naive()
        db.session.commit()
    session.pop("session_token", None)


def current_user() -> User | None:
    raw = session.get("session_token")
    if not raw:
        return None
    token_hash = hash_session_token(raw)
    row = AuthSession.query.filter_by(session_token_hash=token_hash).first()
    if not row or row.revoked_at:
        return None
    expires = row.expires_at.replace(tzinfo=None) if row.expires_at.tzinfo else row.expires_at
    if expires < _utcnow_naive():
        row.revoked_at = _utcnow_naive()
        db.session.commit()
        return None
    return db.session.get(User, row.user_id)


def auth_required(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


_attempt_bucket: dict[str, list[float]] = {}


def rate_limit(limit: int = 10, window_seconds: int = 60):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            import time

            key = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            now = time.time()
            bucket = _attempt_bucket.get(key, [])
            bucket = [x for x in bucket if now - x <= window_seconds]
            if len(bucket) >= limit:
                return jsonify({"error": "Too many requests. Please try again shortly."}), 429
            bucket.append(now)
            _attempt_bucket[key] = bucket
            return fn(*args, **kwargs)

        return wrapper

    return decorator
