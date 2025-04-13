import json
from bs4 import BeautifulSoup as bs
from pydantic import BaseModel

from app.gemini import summarize
from app.config import AI_PROMPT


def innerText(html: str) -> str:
    return bs(html).text


def allHrefs(html: str) -> list[str]:
    return list(
        filter(
            lambda x: x is not None,
            [str(link.get("href")) if link.get("href") else "" for link in bs(html).find_all("a")],
        )
    )


class Summary(BaseModel):
    summary: str
    notes: list[str]
    references: list[dict[str, str]]
    error_msg: str | None = None
    error: bool = False
    activeTime: int | None = None
    backgroundTime: int | None = None


def ai_summarize(text: str) -> Summary:
    try:
        data = json.loads(summarize(text, AI_PROMPT))
        return Summary(**data)
    except Exception as e:
        return Summary(error=True, summary="", notes=[], refrences=[], error_msg=f"Oops!! Failed to summarize. {e}")
