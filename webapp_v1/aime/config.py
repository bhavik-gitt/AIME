import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
WEBAPP_DIR = BASE_DIR / "webapp_v1"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{(WEBAPP_DIR / 'aime.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_BYTES", 16 * 1024 * 1024))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    API_PREFIX = "/api/v1"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",") if o.strip()]
    AUTO_SAVE_ANALYSIS = os.getenv("AUTO_SAVE_ANALYSIS", "false").lower() == "true"
    RESET_TOKEN_TTL_MINUTES = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "30"))
