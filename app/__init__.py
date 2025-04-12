from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from app.config import Config
from flask_cors import CORS
from flask_migrate import Migrate
import ipfsapi

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
)

ipfsclient = ipfsapi.Client(host="localhost", port=5001)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    # Talisman(app, content_security_policy=None)  # Sets secure headers

    from app.routes import bp

    app.register_blueprint(bp, url_prefix="/api")
    CORS(app)
    Migrate(app, db)

    @app.route("/")
    def index2():
        return "Welcome to Homepage"

    return app
