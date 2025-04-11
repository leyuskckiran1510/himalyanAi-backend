import json
from bs4 import BeautifulSoup as bs
from pydantic import BaseModel

from app.gemini import summarize


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
    error: bool = False
    summary: str
    notes: list[str]
    refrences: list[dict[str, str]]
    error_msg: str | None = None


def ai_summarize(text: str) -> Summary:
    try:
        return Summary(**json.loads(summarize(text)))
    except Exception:
        return Summary(error=True, summary="", notes=[], refrences=[], error_msg="Oops!! Failed to summarize.")
