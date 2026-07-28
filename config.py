from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Fake News Detection API"
    environment: str = "development"
    models_dir: str = "models"
    data_dir: str = "data"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
