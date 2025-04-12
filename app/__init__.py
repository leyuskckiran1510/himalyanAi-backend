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
from functools import lru_cache

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
)

ipfsclient = ipfsapi.Client(host="localhost", port=5001)

@lru_cache()
def get_app():
    return Flask(__name__)

def create_app():
    app = get_app()
    app.config.from_object(Config)
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    db.init_app(app)  # This line is missing
    jwt.init_app(app)
    limiter.init_app(app)
    # Talisman(app, content_security_policy=None)  # Sets secure headers

    from app.routes import bp
    app.register_blueprint(bp, url_prefix="/api")
    CORS(app)
    
    # Initialize the database
    with app.app_context():
        db.create_all()
    
    Migrate(app, db)

    @app.route("/")
    def index2():
        return "Welcome to Homepage"
    
    return app
