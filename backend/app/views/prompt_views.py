"""View: Format prompt data for API responses."""

from app.models.prompt import Prompt


def prompt_to_json(prompt: Prompt) -> dict:
    """Format a single prompt for JSON response."""
    return prompt.to_dict()


def prompts_to_json(prompts: list[Prompt]) -> list[dict]:
    """Format a list of prompts for JSON response."""
    return [prompt_to_json(p) for p in prompts]
