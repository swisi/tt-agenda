import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tt_agenda_v2.db")
    AUTO_CREATE_DB = os.environ.get("AUTO_CREATE_DB", "true").lower() == "true"
    CREATE_DEFAULT_USERS = os.environ.get("CREATE_DEFAULT_USERS", "true").lower() == "true"
    CREATE_DEFAULT_POSITIONS = os.environ.get("CREATE_DEFAULT_POSITIONS", "true").lower() == "true"

    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")

    DEFAULT_COACH_USERNAME = os.environ.get("DEFAULT_COACH_USERNAME", os.environ.get("DEFAULT_USER_USERNAME", "coach"))
    DEFAULT_COACH_PASSWORD = os.environ.get("DEFAULT_COACH_PASSWORD", os.environ.get("DEFAULT_USER_PASSWORD", "coach"))
    # Optional token required by clients to connect to WebSocket live channel
    WS_AUTH_TOKEN = os.environ.get("WS_AUTH_TOKEN")
