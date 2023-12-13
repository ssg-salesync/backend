from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.models import db


migration = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migration.init_app(app, db)

    from .api import categories

    app.register_blueprint(categories.bp)

    return app
