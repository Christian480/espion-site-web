from flask import Flask

from database.db import init_db
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.main_routes import main_bp


DEFAULT_CONFIG = {
    "SECRET_KEY": "shadowcomm-secret",
    "DATABASE": "shadowcomm.db",
    "CAESAR_KEY": 3,
    "AUTO_INIT_DB": False,
}


def _configure_app(app, test_config=None):
    app.config.update(DEFAULT_CONFIG)

    if test_config is not None:
        app.config.update(test_config)


def _init_database_if_needed(app):
    if app.config["AUTO_INIT_DB"]:
        init_db(app.config["DATABASE"])


def _register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)


def create_app(test_config=None):
    app = Flask(__name__)

    _configure_app(app, test_config)
    _init_database_if_needed(app)
    _register_blueprints(app)

    return app


app = create_app()


if __name__ == "__main__":
    init_db(app.config["DATABASE"])
    app.run(debug=True)