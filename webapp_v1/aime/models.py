from __future__ import annotations

from datetime import datetime, timedelta, UTC
import secrets

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    account_status = db.Column(db.String(20), nullable=False, default="active", index=True)

    preferences = db.relationship("UserPreference", uselist=False, back_populates="user", cascade="all, delete-orphan")
    analyses = db.relationship("EmotionAnalysis", back_populates="user", cascade="all, delete-orphan")
    sessions = db.relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")


class UserPreference(TimestampMixin, db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    theme = db.Column(db.String(20), nullable=False, default="dark")
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=True)
    privacy_level = db.Column(db.String(30), nullable=False, default="standard")
    auto_save_analysis = db.Column(db.Boolean, nullable=False, default=False)
    retention_days = db.Column(db.Integer, nullable=False, default=90)

    user = db.relationship("User", back_populates="preferences")


class EmotionAnalysis(TimestampMixin, db.Model):
    __tablename__ = "emotion_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    modality = db.Column(db.String(20), nullable=False, index=True)
    predicted_emotion = db.Column(db.String(50), nullable=False, index=True)
    confidence_score = db.Column(db.Float, nullable=False)
    class_probabilities = db.Column(db.JSON, nullable=True)
    model_version = db.Column(db.String(120), nullable=False, default="v1")
    processing_status = db.Column(db.String(30), nullable=False, default="completed", index=True)
    duration_seconds = db.Column(db.Float, nullable=True)

    user = db.relationship("User", back_populates="analyses")
    notes = db.relationship("AnalysisNote", back_populates="analysis", cascade="all, delete-orphan")


class AnalysisNote(TimestampMixin, db.Model):
    __tablename__ = "analysis_notes"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("emotion_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_reported_mood = db.Column(db.String(50), nullable=True)
    personal_reflection = db.Column(db.Text, nullable=True)

    analysis = db.relationship("EmotionAnalysis", back_populates="notes")


class AuthSession(TimestampMixin, db.Model):
    __tablename__ = "auth_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token_hash = db.Column(db.String(128), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)

    user = db.relationship("User", back_populates="sessions")

    @staticmethod
    def new_expiry(hours: int = 24) -> datetime:
        return datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=hours)


class PasswordResetToken(TimestampMixin, db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @staticmethod
    def generate() -> str:
        return secrets.token_urlsafe(32)
