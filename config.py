import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/expense_tracker_latest')
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/expense_tracker_test'
