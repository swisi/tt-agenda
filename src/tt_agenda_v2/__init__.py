from flask import Flask

from .config import Config
from .infrastructure.in_memory_user_repository import InMemoryUserRepository
from .interface.http.routes import register_routes


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.extensions["user_repository"] = InMemoryUserRepository.create_with_defaults(
        admin_username=app.config["DEFAULT_ADMIN_USERNAME"],
        admin_password=app.config["DEFAULT_ADMIN_PASSWORD"],
        user_username=app.config["DEFAULT_USER_USERNAME"],
        user_password=app.config["DEFAULT_USER_PASSWORD"],
    )

    register_routes(app)
    return app
