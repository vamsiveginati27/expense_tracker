from pydantic import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    mongodb_uri: str
    jwt_secret_key: str
    openai_api_key: str
    tavily_api_key: str
    anthropic_api_key: str
    expense_api_base_url: str = "http://localhost:5002/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()