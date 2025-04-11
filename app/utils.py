import html
from string import printable
from random import choices


def sanitize_output(data: dict) -> dict:
    """HTML-escape all string values (for extra safety if needed)."""
    return {k: html.escape(str(v)) if isinstance(v, str) else v for k, v in data.items()}


def generate_password(length: int) -> str:
    non_white_spaces = printable.strip()
    return "".join(choices(non_white_spaces, k=length))


def normalize_ai_response(text: str) -> str:
    return text.replace("```json", "", 1).rstrip("```").strip()
