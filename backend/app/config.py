"""Application configuration classes."""
import os
from datetime import timedelta


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # File uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # AI Verifier: 'mock' | 'google_vision' | 'aws_rekognition'
    AI_VERIFIER_TYPE = os.environ.get('AI_VERIFIER_TYPE', 'mock')

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Leaderboard cache TTL (seconds)
    LEADERBOARD_CACHE_TTL = 300  # 5 minutes

    # Quest settings
    DAILY_QUEST_COUNT = 3

    # Challenge settings
    CHALLENGE_COST_POINTS = 10
    CHALLENGE_REWARD_GEMS = 5
    CHALLENGE_DURATION_MINUTES = 60


class DevelopmentConfig(BaseConfig):
    """Development configuration — uses SQLite for easy local dev."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'akd_dev.db')
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """Production configuration — requires Postgres."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Override secret keys from environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


class PythonAnywhereConfig(BaseConfig):
    """PythonAnywhere deployment — SQLite by default, MySQL via DATABASE_URL."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'akd.db')
    )
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-on-pythonanywhere')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-jwt-on-pythonanywhere')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'pythonanywhere': PythonAnywhereConfig,
}
