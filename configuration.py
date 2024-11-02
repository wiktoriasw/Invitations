from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    sqlalchemy_database_url: str = "sqlite:///./sql_app.db"
    secret_key: str
    algorithm: str = "HS256"


settings = Settings()
