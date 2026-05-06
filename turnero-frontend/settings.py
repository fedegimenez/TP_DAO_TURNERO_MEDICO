import os
import warnings

_DEFAULT_SECRET_KEY = "dev-secret-change-me"


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")  # FastAPI backend
    DEBUG = os.environ.get("DEBUG", "1") == "1"

    if not SECRET_KEY:
        warnings.warn(
            "SECRET_KEY not set! Using insecure default. "
            "Set the SECRET_KEY environment variable to a strong, random value in production.",
            stacklevel=2,
        )
        SECRET_KEY = _DEFAULT_SECRET_KEY


settings = Settings()
