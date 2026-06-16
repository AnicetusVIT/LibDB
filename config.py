# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "LibDB"
    app_name: str = "LibDB Resource Engine"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()