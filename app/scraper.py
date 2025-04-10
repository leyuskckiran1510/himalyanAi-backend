from typing import TypedDict
from bs4 import BeautifulSoup as bs
import requests

SCRAPER_API = "https://duckduckgo.com/duckchat/v1/chat"
headers = {
    "accept": "text/event-stream",
    "accept-language": "en-US,en;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://duckduckgo.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://duckduckgo.com/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    # TODO: use proper api endpoints for summarizing
    # the content instead of hijacking the duckduckgo chat application
    "x-fe-version": "serp_20250410_071825_ET-227034fa144d75d4af83",
    "x-vqd-4": "4-32475679058140722245001985009606782232",
    "x-vqd-hash-1": "eyJzZXJ2ZXJfaGFzaGVzIjpbInhMVFZ6Nytqb3BnaTNyOFFJQXVIdnBOYjhxQ0NYSmoxdVNjS21wb0hpTVk9IiwiNzdONmVSNmNyUmQxQy8zY2FSc05jTzE3SERlYzAvZTNYYnhRNXF3NTJ0ND0iXSwiY2xpZW50X2hhc2hlcyI6WyJIWWxpM21BWEhtSHQvSHJJQjljU1BJK2h3SW9aUzIvRWtnb2x2NDVqY01RPSIsIkkrTENFQm05SW1TUWRaV1BkZEZ2djAxeVJVK1RyODJEbnJKMmRlUTFueW89Il0sInNpZ25hbHMiOnt9LCJtZXRhIjp7InYiOiIxIiwiY2hhbGxlbmdlX2lkIjoiN2Q5ZjY1ZDAxMmViOTkyNWVhYzRiZmU0YzgwMzQzMWVmZGY1ZGJjOTY3Nzc2NTk0OWRlNWFkODkyNzk2YjkyOWg4amJ0Iiwib3JpZ2luIjoiaHR0cHM6Ly9kdWNrZHVja2dvLmNvbSIsInN0YWNrIjoiRXJyb3JcbmF0IGtlIChodHRwczovL2R1Y2tkdWNrZ28uY29tL2Rpc3Qvd3BtLmNoYXQuMjI3MDM0ZmExNDRkNzVkNGFmODMuanM6MTozMDA5MClcbmF0IGFzeW5jIGRpc3BhdGNoU2VydmljZUluaXRpYWxWUUQgKGh0dHBzOi8vZHVja2R1Y2tnby5jb20vZGlzdC93cG0uY2hhdC4yMjcwMzRmYTE0NGQ3NWQ0YWY4My5qczoxOjQ1NjQwKSJ9fQ==",
}


class _apiData(TypedDict):
    role: str
    content: str


class ApiData(TypedDict):
    model: str
    messages: list[_apiData]


data_dict: ApiData = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": """
             i will give you a big conentent 
             summarize the content into short brife summary, with bullet points 
             and notes. And it must be in markdown 


             
             remember it must be in markdown so i can instert it directly 
             
            
             this is the content to be summarized 
             
             {data_to_summarize}""",
        },
    ],
}


def innerText(html: str) -> str:
    return bs(html).text


def allHrefs(html: str) -> list[str]:
    return list(filter(lambda x: x is not None, [link.get("href") for link in bs(html).find_all("a")]))


def summarize(text: str) -> str:
    __data = data_dict
    __data["messages"][0]["content"] = __data["messages"][0]["content"].format_map({"data_to_summarize": text})
    response = requests.post(SCRAPER_API, data=__data, headers=headers, stream=True)
    if response.status_code == 200:
        content = ""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                content += chunk.decode("utf-8")
        return content
    return "error getting summary"
