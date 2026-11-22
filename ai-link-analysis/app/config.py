from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Website Link Analysis API"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"
    max_html_bytes: int = 2_000_000
    max_text_chars: int = 18_000
    request_timeout_seconds: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
