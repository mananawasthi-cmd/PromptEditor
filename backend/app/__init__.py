import os
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from app.controllers.chat_controller import chat_bp
from app.controllers.prompts_controller import prompts_bp
from app.controllers.tts_controller import tts_bp


def create_app():
    app = Flask(__name__, static_folder=None)

    # CORS: allow all in production; set CORS_ORIGINS for dev (e.g. http://localhost:5173)
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    if cors_origins == "*":
        CORS(app)
    else:
        CORS(app, origins=[o.strip() for o in cors_origins.split(",")])

    app.register_blueprint(prompts_bp, url_prefix="/api")
    app.register_blueprint(tts_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    # Serve frontend static files (production only, when static dir exists)
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            if path and (static_dir / path).is_file():
                return send_from_directory(static_dir, path)
            return send_from_directory(static_dir, "index.html")

    return app
