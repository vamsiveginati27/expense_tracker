from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jwt_secret_key: str = "dev-secret-key-change-in-production"
    mongodb_uri: str = "mongodb://localhost:27017/expense_tracker_latest"
    anthropic_api_key: str = ""
    google_api_key: str = ""
    openai_api_key: str = ""
    tavily_api_key: str = ""
    expense_api_base_url: str = "http://localhost:5002/api"
    debug: bool = False
    testing: bool = False


settings = Settings()


class Config:
    JWT_SECRET_KEY = settings.jwt_secret_key
    MONGODB_URI = settings.mongodb_uri
    TESTING = settings.testing
    DEBUG = settings.debug


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    MONGODB_URI = "mongodb://localhost:27017/expense_tracker_test"
