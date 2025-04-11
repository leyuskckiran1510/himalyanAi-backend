from flask import jsonify
import requests
import json
from app.config import AI_PROMPT
from app.mn import MODELS_LIST
from dotenv import load_dotenv
import os

from app.utils import normalize_ai_response
from pydantic import BaseModel


class __Message(BaseModel):
    role: str
    content: str
    refusal: None | str
    reasoning: None | str


class __Choice(BaseModel):
    logprobs: None | str
    finish_reason: str
    native_finish_reason: str
    index: int
    message: __Message


class __PromptTokensDetails(BaseModel):
    cached_tokens: int


class __CompletionTokensDetails(BaseModel):
    reasoning_tokens: int


class __Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: __PromptTokensDetails
    completion_tokens_details: __CompletionTokensDetails


class __ChatCompletion(BaseModel):
    id: str
    provider: str
    model: str
    object: str
    created: int
    choices: list[__Choice]
    system_fingerprint: str
    usage: __Usage


load_dotenv()

__CHAT_AI_API = "https://openrouter.ai/api/v1/chat/completions"
__CHAT_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('OPEN_ROUTER','')}",
}


def summarize(text: str) -> str:
    data = {
        "model": MODELS_LIST[0],
        "messages": [
            {
                "role": "user",
                "content": AI_PROMPT + text,
            }
        ],
    }

    response = requests.post(__CHAT_AI_API, data=json.dumps(data), headers=__CHAT_HEADERS, stream=True)
    if response.status_code == 200:
        _json = response.json()
        try:
            content = ""
            for choice in __ChatCompletion(**_json).choices:
                content += choice.message.content
            return normalize_ai_response(content)
        except Exception as e:
            pass
    return "error getting summary"


"""
Expected output

{
   "id":"gen-1744351872-ojr2EdBd8GbovEz0BUKo",
   "provider":"Novita",
   "model":"deepseek/deepseek-r1",
   "object":"chat.completion",
   "created":1744351872,
   "choices":[
      {
         "logprobs":null,
         "finish_reason":"stop",
         "native_finish_reason":"stop",
         "index":0,
         "message":{
            "role":"assistant",
            "content":"A",
            "refusal":null,
            "reasoning":"Okay, let me start by understanding the user's request. They want me to summarize a lengthy text about using BeautifulSoup to extract href attributes from anchor tags. The summary should be in markdown, concise, with additional notes and reference links.\n\nFirst, I need to parse the provided content. There are three sources: GeeksForGeeks, 极客教程 (Geek Docs), and Techjury. Each explains how to get href attributes using BeautifulSoup but in different languages and depths. \n\nFrom GeeksForGeeks, the key points are using BeautifulSoup to find all anchor tags and extract hrefs starting with \"https://\". They mention the library needs external installation. \n\n极客教程's content is in Chinese, so I'll need to translate the main idea. It's about using BeautifulSoup to parse HTML and access the 'href' attribute of 'a' elements. They might have code examples using find or find_all methods.\n\nTechjury's article likely covers similar steps: importing BeautifulSoup, parsing HTML, finding 'a' tags, and accessing the href attribute. They might emphasize common use cases like web scraping.\n\nNext, I should structure the summary. Start with a brief introduction on the method. Then list the steps concisely. Code examples are essential, so including a simple example using find_all('a') and getting 'href' with get('href'). \n\nAdditional notes should mention checking for existence of 'href' to avoid errors, handling relative URLs by joining with base URL, and filtering specific links using attributes like href starting with certain strings.\n\nReference links should point to the provided URLs. Need to ensure the markdown is clean without extra text. Check for conciseness, making sure each section is digestible. Avoid any markdown formatting in the notes or references beyond what's specified.\n\nWait, the user also mentioned to not include any other text like \"here is your output\". So I need to make sure the response is just the markdown content. Let me verify
that each part adheres to the requirements. Also, ensure that the code example is properly formatted in markdown. Maybe use backticks for the code block.\n\nDouble-check
if all three sources are covered in the summary. The GeeksForGeeks link talks about scraping links starting with \"https://\", which is a useful tip. The Chinese site explains the basics of using BeautifulSoup for this purpose. Techjury's contribution might be a general step-by-step guide.\n\nPutting it all together: the summary should encapsulate the method, steps, a code example, notes on best practices, and references. Make sure each part is brief but informative. Avoid redundancy between the sources,
focusing on the common techniques they all mention.\n\nI think that's all. Time to draft the markdown.\n"
         }
      }
   ],
   "system_fingerprint":"",
   "usage":{
      "prompt_tokens":470,
      "completion_tokens":915,
      "total_tokens":1385,
      "prompt_tokens_details":{
         "cached_tokens":0
      },
      "completion_tokens_details":{
         "reasoning_tokens":567
      }
   }
}
"""


if __name__ == "__main__":
    summary = summarize(
        """
    get('href') method returns the value of the href attribute of the anchor tag.. By ...


    Only include results for this site
    Hide site from these results
    Share feedback about this site

    GeeksForGeeks

    https://www.geeksforgeeks.org › beautifulsoup-scraping-link-from-html

    BeautifulSoup - Scraping Link from HTML - GeeksforGeeks
    bs4 (BeautifulSoup): It is a library in python which makes it easy to scrape information from web pages, and helps in extracting the data from HTML and XML files. This library needs to be downloaded externally as it does not come readily with Python package. ... # find all the anchor tags with "href" # attribute starting with "https://" for ...


    Only include results for this site
    Hide site from these results
    Share feedback about this site

    极客教程

    https://geek-docs.com › beautifulsoup › beautifulsoup-questions › 119_beautifulsoup_python_beautifulsoup_how_to_get_href_attribute_of_a_element.html

    BeautifulSoup ：如何获取'a'元素的'href'属性|极客教程
    BeautifulSoup ：如何获取'a'元素的'href'属性 在本文中，我们将介绍如何使用Python的BeautifulSoup库来获取HTML代码中的'a'元素的'href'属性。 阅读更多：BeautifulSoup 教程 什么是BeautifulSoup？ BeautifulSoup是一个用于解析HTML和XML等标记语言的Python库。它可以很方便地从网页中提取所需的数据


    Only include results for this site
    Hide site from these results
    Share feedback about this site

    Techjury

    https://techjury.net › blog › how-to-get-an-href-attribute-using-beautifulsoup


              """
    )

    print(summary)
