from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS


jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')

    CORS(app, resources={r"/*": {"origins": "*"}})

    jwt.init_app(app)

    from .api import main, dashboard

    app.register_blueprint(main.bp)
    app.register_blueprint(dashboard.bp)

    return app

