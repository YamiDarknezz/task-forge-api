import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Application
    APP_NAME = os.getenv('APP_NAME', 'TaskForge API')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Flask
    FLASK_APP = os.getenv('FLASK_APP', 'run.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = False
    TESTING = False

    # Database - Azure SQL Server
    AZURE_SQL_SERVER = os.getenv('AZURE_SQL_SERVER')
    AZURE_SQL_DATABASE = os.getenv('AZURE_SQL_DATABASE', 'taskforge_db')
    AZURE_SQL_USER = os.getenv('AZURE_SQL_USER')
    AZURE_SQL_PASSWORD = os.getenv('AZURE_SQL_PASSWORD')
    AZURE_SQL_PORT = os.getenv('AZURE_SQL_PORT', '1433')

    driver = 'ODBC Driver 17 for SQL Server'

    if all([AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USER, AZURE_SQL_PASSWORD]):
        SQLALCHEMY_DATABASE_URI = (
            f"mssql+pyodbc://{AZURE_SQL_USER}:{AZURE_SQL_PASSWORD}@"
            f"{AZURE_SQL_SERVER}:{AZURE_SQL_PORT}/{AZURE_SQL_DATABASE}"
            f"?driver={driver.replace(' ', '+')}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///taskforge.db'

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_JSON_KEY = 'identity'
    JWT_ERROR_MESSAGE_KEY = 'message'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200 per day;50 per hour')
    RATELIMIT_HEADERS_ENABLED = True

    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 10))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'

    # Allow SQLite in production for now, but should use Azure SQL Database
    # The SQLALCHEMY_DATABASE_URI is inherited from Config class
    # To use Azure SQL, configure these environment variables:
    # AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USER, AZURE_SQL_PASSWORD


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
