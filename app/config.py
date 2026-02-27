import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trainings.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WEBHOOK_ENABLED = os.environ.get('WEBHOOK_ENABLED', 'false').lower() == 'true'
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://n8n.3624.ch/webhook/messaging')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    AUTO_CREATE_DB = os.environ.get('AUTO_CREATE_DB', 'true').lower() == 'true'
    CREATE_DEFAULT_USERS = os.environ.get('CREATE_DEFAULT_USERS', 'false').lower() == 'true'
    DEFAULT_ADMIN_USERNAME = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin')
    DEFAULT_USER_USERNAME = os.environ.get('DEFAULT_USER_USERNAME', 'user')
    DEFAULT_USER_PASSWORD = os.environ.get('DEFAULT_USER_PASSWORD', 'user')
    
    logger.info(f"WEBHOOK_ENABLED env: {os.environ.get('WEBHOOK_ENABLED')}, parsed: {WEBHOOK_ENABLED}")
    logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")
    logger.info(f"LOG_LEVEL: {LOG_LEVEL}")
