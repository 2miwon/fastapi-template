from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    JWT_ALG: str = "HS256"
    JWT_SECRET: str
    JWT_EXP: int = 60 * 24  # minutes


auth_settings = AuthConfig()
