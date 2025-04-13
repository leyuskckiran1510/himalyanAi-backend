import json
from dotenv import load_dotenv
import os

import requests
from app.config import AI_PROMPT
from pydantic import BaseModel

from app.utils import normalize_ai_response


class GM_Part(BaseModel):
    text: str


class GM_Content(BaseModel):
    parts: list[GM_Part]
    role: str


class GM_Candidate(BaseModel):
    content: GM_Content
    finishReason: str
    avgLogprobs: float | None


class GM_TokenDetail(BaseModel):
    modality: str
    tokenCount: int


class GM_UsageMetadata(BaseModel):
    promptTokenCount: int
    candidatesTokenCount: int
    totalTokenCount: int
    promptTokensDetails: list[GM_TokenDetail]
    candidatesTokensDetails: list[GM_TokenDetail]


class GM_ResponseModel(BaseModel):
    candidates: list[GM_Candidate]
    usageMetadata: GM_UsageMetadata
    modelVersion: str


load_dotenv()
__CHAT_AI_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ.get('GOOGLE','')}"
__CHAT_HEADERS = {"Content-Type": "application/json"}


def summarize(text: str, prompt_choise: str = AI_PROMPT) -> str:
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_choise + text,
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
    # with open("./app/input.txt", "r") as fp:
    print(summarize("https://flask.palletsprojects.com/en/stable/testing/"))
