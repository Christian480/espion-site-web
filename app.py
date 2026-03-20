from flask import Flask

from database.db import init_db
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.main_routes import main_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "shadowcomm-secret"
    app.config["DATABASE"] = "shadowcomm.db"
    app.config["CAESAR_KEY"] = 3

    if test_config is not None:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)