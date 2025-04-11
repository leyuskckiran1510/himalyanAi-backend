from app.utils import generate_password


class Config:
    SECRET_KEY = generate_password(64)
    SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = generate_password(64)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True


AI_PROMPT = """
Hi you are a recall ai. With following purpose
- summarize the very long text content given to you
- make it into a json
- don't spit out any other text like,(eg.  here is your output and others)
- just the actual output not blafing
- it most be consie and digestiable
- and at end write additonal notes 
- provide refrece links for further deep studies
- don't stylizie it with markdown, just raw json text,
  no need to put it inside code block
the response must be on follwoing format

{
        "summary":"text only"
        "notes":["text","text", ...],
        "refrences":[{"name":"link"},...]
}


So here is your text content


"""
