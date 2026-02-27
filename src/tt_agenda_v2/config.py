import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")

    DEFAULT_USER_USERNAME = os.environ.get("DEFAULT_USER_USERNAME", "user")
    DEFAULT_USER_PASSWORD = os.environ.get("DEFAULT_USER_PASSWORD", "user")
