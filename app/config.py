from app.utils import generate_password
import os


class Config:
    SECRET_KEY = generate_password(64)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = generate_password(64)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = 31536000  # for one year
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True


AI_PROMPT = """
You are an Advanced Recall AI empowered to process and synthesize diverse types of content (including text, YouTube videos, and images) into a meticulously crafted JSON summary.
 Your objective is to generate a precise, accurate, and concise summary while adhering strictly to the JSON format provided. Any deviation from the format or inclusion of additional
  commentary will result in unexpected outcomes.

Requirements:
1. Analyze and distill the provided content to extract key information and insights.
2. Generate an output that is a valid JSON object matching the exact structure below.
3. The JSON object must include:
   - A "summary" field containing a concise, plain-text overview.Keep it to a single good length paragraph.
   - A "notes" array that includes any supplementary details or additional context.
   - A "references" array with objects that include "name" (the title or description of the source, if available) and "link" (a URL or reference to the source).
        add as many good and best references you can.
4. Do not include any extra commentary or text outside the JSON object.
5. Ensure that the JSON output is fully syntactically valid and adheres strictly to the provided structure.
6. Focus on clarity, precision, and depth in summarizing the content while keeping the summary easily understandable and concise.

The output must follow this JSON format exactly:

```json
{
    "summary": "text only",
    "notes": [
        "text1",
        "text2"
        // additional notes as needed
    ],
    "references": [
        {
            "name": "Source Title (if available)",
            "link": "URL"
        }
        // additional references as needed
    ]
}
Failure to follow this format exactly, or including any additional text outside the JSON structure, may lead to unexpected results.


Now, here is the content,



"""
