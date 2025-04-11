import json
from dotenv import load_dotenv
import os

import requests
from app.config import AI_PROMPT
from pydantic import BaseModel

from app.utils import normalize_ai_response


class __Part(BaseModel):
    text: str


class __Content(BaseModel):
    parts: list[__Part]
    role: str


class __Candidate(BaseModel):
    content: __Content
    finishReason: str
    avgLogprobs: float | None


class __TokenDetail(BaseModel):
    modality: str
    tokenCount: int


class __UsageMetadata(BaseModel):
    promptTokenCount: int
    candidatesTokenCount: int
    totalTokenCount: int
    promptTokensDetails: list[__TokenDetail]
    candidatesTokensDetails: list[__TokenDetail]


class GM_ResponseModel(BaseModel):
    candidates: list[__Candidate]
    usageMetadata: __UsageMetadata
    modelVersion: str


load_dotenv()
__CHAT_AI_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ.get('GOOGLE','')}"
__CHAT_HEADERS = {"Content-Type": "application/json"}


def summarize(text: str) -> str:
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": AI_PROMPT + text,
                    },
                ]
            }
        ]
    }
    response = requests.post(__CHAT_AI_API, data=json.dumps(data), headers=__CHAT_HEADERS)
    if response.status_code == 200:
        _json = response.json()
        try:
            response_model = GM_ResponseModel(**_json)
            content = ""
            for candidate in response_model.candidates:
                for part in candidate.content.parts:
                    content += part.text
            return normalize_ai_response(content)
        except Exception:
            pass
    return "error getting summary\n"


"""
Expected json output from gemenie
{
   "candidates":[
      {
         "content":{
            "parts":[
               {
                  "text":""
                  }
            ],
            "role":"model"
         },
         "finishReason":"STOP",
         "avgLogprobs":0
      }
   ],
   "usageMetadata":{
      "promptTokenCount":508,
      "candidatesTokenCount":273,
      "totalTokenCount":781,
      "promptTokensDetails":[
         {
            "modality":"TEXT",
            "tokenCount":508
         }
      ],
      "candidatesTokensDetails":[
         {
            "modality":"TEXT",
            "tokenCount":273
         }
      ]
   },
   "modelVersion":"gemini-2.0-flash"
}
"""

if __name__ == "__main__":
    print(
        summarize(
            """
                    # Extracting href Attributes with BeautifulSoup

## Summary
- **Method**: Use `get('href')` on anchor tags to extract URL values
- **Key Steps**:
  1. Parse HTML with BeautifulSoup
  2. Find all `<a>` tags using `find_all('a')`
  3. Access href values using `.get('href')`
  4. Filter links using attribute selectors (e.g., `href^=\"https://\"`)

## Code Example
```python
from bs4 import BeautifulSoup

html = '''<a href=\"https://example.com\">Link</a>'''
soup = BeautifulSoup(html, 'html.parser')

for link in soup.find_all('a'):
    print(link.get('href'))  # Output: https://example.com
```

## Additional Notes
1. Always check if `href` exists before accessing to avoid `NoneType` errors
2. Use `urljoin` to handle relative URLs (e.g., `/page.html`)
3. Combine with regex for advanced pattern matching in href attributes

## References
- [GeeksForGeeks: Link Scraping Guide](https://www.geeksforgeeks.org/beautifulsoup-scraping-link-from-html)
- [Geek Docs: href Attribute Extraction](https://geek-docs.com/beautifulsoup/beautifulsoup-questions/119_beautifulsoup_python_beautifulsoup_how_to_get_href_attribute_of_a_element.html)
- [Techjury Tutorial](https://techjury.net/blog/how-to-get-an-href-attribute-using-beautifulsoup)


"""
        )
    )
