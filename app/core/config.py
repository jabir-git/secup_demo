from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me-in-production-supersecretkey123456789"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///./secup.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
