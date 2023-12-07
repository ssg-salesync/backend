from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
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
