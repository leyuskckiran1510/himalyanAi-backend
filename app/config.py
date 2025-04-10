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
