from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Turnero Backend"
    BACKEND_CORS_ORIGINS: List[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    # SQLite default is for local development only — not suitable for production.
    DATABASE_URL: str = "sqlite:///./turnero.db"
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_must_be_changed(cls, v: str) -> str:
        if v in ("change-me", ""):
            raise ValueError(
                "JWT_SECRET must be set to a secure value via the JWT_SECRET environment "
                "variable. Refusing to start with the insecure default."
            )
        return v

settings = Settings()
