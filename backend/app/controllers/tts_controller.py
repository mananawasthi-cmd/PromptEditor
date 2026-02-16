import os

import requests
from flask import Blueprint, request, Response

tts_bp = Blueprint("tts", __name__)

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"


@tts_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech using ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        return {"error": "ELEVENLABS_API_KEY not configured"}, 500

    data = request.get_json() or {}
    text = data.get("text", "").strip()
    voice_id = data.get("voice_id", "").strip()
    speed = float(data.get("speed", 1.0))
    speed = max(0.5, min(2.0, speed))

    if not text:
        return {"error": "Text is required"}, 400
    if not voice_id:
        return {"error": "Voice ID is required"}, 400

    url = f"{ELEVENLABS_URL}/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": speed},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if not resp.ok:
            err = resp.json().get("detail", {}).get("message", resp.text) or resp.text
            return {"error": err}, resp.status_code
        return Response(resp.content, mimetype="audio/mpeg")
    except requests.RequestException as e:
        return {"error": str(e)}, 500
