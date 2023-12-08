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
    item_app = Flask(__name__)
    item_app.config.from_envvar('APP_CONFIG_FILE')

    CORS(item_app)

    db.init_app(item_app)
    bcrypt.init_app(item_app)
    jwt.init_app(item_app)
    migration.init_app(item_app, db)

    from .api import categories, items

    # item_app.register_blueprint(categories.bp)
    # item_app.register_blueprint(items.bp)

    return item_app
