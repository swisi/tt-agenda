import os
import logging

logger = logging.getLogger(__name__)

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trainings.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    WEBHOOK_ENABLED = os.environ.get('WEBHOOK_ENABLED', 'false').lower() == 'true'
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://n8n.3624.ch/webhook/messaging')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    logger.info(f"WEBHOOK_ENABLED env: {os.environ.get('WEBHOOK_ENABLED')}, parsed: {WEBHOOK_ENABLED}")
    logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")
    logger.info(f"LOG_LEVEL: {LOG_LEVEL}")
