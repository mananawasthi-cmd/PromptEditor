"""Chat controller for LLM-powered prompt editing via Groq."""
import json
import os

from flask import Blueprint, Response, request, stream_with_context
from groq import Groq

chat_bp = Blueprint("chat", __name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
# llama-3.1-8b-instant: 500K TPD (free tier). llama-3.3-70b: 100K TPD.
MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
FALLBACK_MODEL = "llama-3.3-70b-versatile"


def _stream_chat(messages):
    """Stream chat completion from Groq."""
    if not GROQ_API_KEY:
        yield "data: " + json.dumps({"error": "GROQ_API_KEY not configured. Add it to backend/.env"}) + "\n\n"
        return

    client = Groq(api_key=GROQ_API_KEY)
    for model in [MODEL, FALLBACK_MODEL]:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=8192,
                stream=True,
            )
            for chunk in completion:
                delta = chunk.choices[0].delta.content if chunk.choices else ""
                if delta:
                    yield "data: " + json.dumps({"content": delta}) + "\n\n"
            return
        except Exception as e:
            if model == FALLBACK_MODEL:
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
            continue


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Stream LLM response for prompt editing. Supports multi-turn via messages history."""
    data = request.get_json() or {}
    prompt_content = data.get("prompt_content", "")
    selected_text = data.get("selected_text", "").strip()
    user_message = data.get("message", "").strip()
    history = data.get("messages", [])  # [{role, content}, ...] for multi-turn

    if not user_message:
        return {"error": "Message is required"}, 400

    if not prompt_content and not selected_text:
        return {"error": "Add your prompt or select text first"}, 400

    system_content = (
        "You are a helpful assistant that edits and improves prompts. "
        "When given a selection, output ONLY the replacement text. "
        "When given the full prompt, output the complete edited prompt. "
        "Preserve formatting unless the user asks to change it. "
        "For follow-up messages, refine the previous edit based on the user's feedback."
    )

    if selected_text:
        base_context = (
            f"The user is editing a prompt. Selected text:\n\n```\n{selected_text}\n```\n\n"
            f"Full prompt:\n\n```\n{prompt_content}\n```\n\n"
        )
    else:
        base_context = (
            f"The user is editing their entire prompt:\n\n```\n{prompt_content}\n```\n\n"
        )

    if history:
        # Multi-turn: build messages from history + new user message
        context_messages = [
            {"role": "system", "content": system_content + "\n\n" + base_context},
            *history,
            {"role": "user", "content": user_message},
        ]
    else:
        # First turn
        context = (
            base_context + f"Their instruction: {user_message}\n\n"
            f"Respond with ONLY the edited/replaced text. Output nothing else."
        )
        context_messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": context},
        ]

    messages = context_messages

    return Response(
        stream_with_context(_stream_chat(messages)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@chat_bp.route("/voice-chat", methods=["POST"])
def voice_chat():
    """Voice chat: user speaks about their pitch, AI responds. For practicing pitches via voice."""
    data = request.get_json() or {}
    prompt_content = data.get("prompt_content", "").strip()
    user_message = data.get("message", "").strip()
    history = data.get("messages", [])

    if not user_message:
        return {"error": "Message is required"}, 400

    if not prompt_content:
        return {"error": "Select a prompt (your pitch) first"}, 400

    system_content = (
        "You are a bot in a live voice call. Your behavior, personality, and how you react are defined by this prompt:\n\n"
        f"```\n{prompt_content}\n```\n\n"
        "IMPORTANT: Respond EXACTLY as the bot/persona described in the prompt above. Mimic a real live call - natural, conversational, reactive.\n"
        "Always respond in casual Hindi (हिंदी) - use everyday spoken Hindi, mix of Hindi and Hinglish if natural. Keep it short (1-3 sentences) for voice."
    )

    if history:
        messages = [
            {"role": "system", "content": system_content},
            *history,
            {"role": "user", "content": user_message},
        ]
    else:
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

    return Response(
        stream_with_context(_stream_chat(messages)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


