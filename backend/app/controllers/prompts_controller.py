from datetime import datetime

from flask import Blueprint, request, jsonify

from app.models.prompt import Prompt
from app.views.prompt_views import prompt_to_json, prompts_to_json

# In-memory store (replace with database in production)
_prompts: list[Prompt] = [
    Prompt(
        title="Welcome",
        content="Write your first prompt here...",
    )
]

prompts_bp = Blueprint("prompts", __name__)


@prompts_bp.route("/prompts", methods=["GET"])
def get_all():
    """Controller: List all prompts."""
    return jsonify(prompts_to_json(_prompts))


@prompts_bp.route("/prompts/<prompt_id>", methods=["GET"])
def get_by_id(prompt_id):
    """Controller: Get a single prompt by ID."""
    prompt = next((p for p in _prompts if p.id == prompt_id), None)
    if not prompt:
        return jsonify({"error": "Not found"}), 404
    return jsonify(prompt_to_json(prompt))


@prompts_bp.route("/prompts", methods=["POST"])
def create():
    """Controller: Create a new prompt."""
    data = request.get_json() or {}
    prompt = Prompt(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
    )
    _prompts.append(prompt)
    return jsonify(prompt_to_json(prompt)), 201


@prompts_bp.route("/prompts/<prompt_id>", methods=["PUT"])
def update(prompt_id):
    """Controller: Update an existing prompt."""
    prompt = next((p for p in _prompts if p.id == prompt_id), None)
    if not prompt:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json() or {}
    if "title" in data:
        prompt.title = data["title"]
    if "content" in data:
        prompt.content = data["content"]
    prompt.updated_at = datetime.utcnow()

    return jsonify(prompt_to_json(prompt))


@prompts_bp.route("/prompts/<prompt_id>", methods=["DELETE"])
def delete(prompt_id):
    """Controller: Delete a prompt."""
    global _prompts
    prompt = next((p for p in _prompts if p.id == prompt_id), None)
    if not prompt:
        return jsonify({"error": "Not found"}), 404
    _prompts = [p for p in _prompts if p.id != prompt_id]
    return "", 204
