import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trainings.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
