from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from .config import Config
from .extensions import db, migrate


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .api.auth import bp as auth_bp
    from .api.analysis import bp as analysis_bp
    from .api.user import bp as user_bp
    from .api.pages import bp as pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix=app.config["API_PREFIX"])
    app.register_blueprint(analysis_bp, url_prefix=app.config["API_PREFIX"])
    app.register_blueprint(user_bp, url_prefix=app.config["API_PREFIX"])

    @app.get("/api/v1/health")
    def health():
        return jsonify({"ok": True})

    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not Found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"error": "Uploaded file is too large"}), 413

    return app
