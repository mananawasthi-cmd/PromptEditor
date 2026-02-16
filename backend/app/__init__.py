from flask import Flask
from flask_cors import CORS

from app.controllers.chat_controller import chat_bp
from app.controllers.prompts_controller import prompts_bp
from app.controllers.tts_controller import tts_bp


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"])

    app.register_blueprint(prompts_bp, url_prefix="/api")
    app.register_blueprint(tts_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app
