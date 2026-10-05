from enum import Enum

from pydantic import ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Environment
    port: int
    database_url: str
    redis_url: str
    log_level: LogLevel
    jwt_secret: str
    cors_origin: str
    api_key_a: str
    api_key_b: str

    @field_validator("database_url", "redis_url", "jwt_secret", "cors_origin", "api_key_a", "api_key_b", mode="before")
    @classmethod
    def require_non_empty(cls, value: str, info):
        if value is None or str(value).strip() == "":
            raise ValueError(f"Missing required environment variable: {info.field_name.upper()}")
        return str(value).strip()

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not (1 <= value <= 65535):
            raise ValueError("Invalid PORT. PORT must be between 1 and 65535.")
        return value

    @field_validator("jwt_secret", "api_key_a", "api_key_b")
    @classmethod
    def validate_secret_length(cls, value: str, info) -> str:
        if len(value) < 32:
            raise ValueError(f"Invalid {info.field_name.upper()}. Must be at least 32 characters.")
        return value

    @model_validator(mode="after")
    def prevent_localhost_in_production(self):
        if self.api_key_a == self.api_key_b:
            raise ValueError("API_KEY_A and API_KEY_B must be distinct.")
        if self.jwt_secret in {self.api_key_a, self.api_key_b}:
            raise ValueError("JWT_SECRET must not be reused as an API key.")
        if self.app_env == Environment.production:
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                raise ValueError(
                    "Invalid DATABASE_URL for production. Must not point to localhost."
                )
            if "localhost" in self.redis_url or "127.0.0.1" in self.redis_url:
                raise ValueError("Invalid REDIS_URL for production. Must not point to localhost.")
        return self


try:
    settings = Settings()
except ValidationError as exc:
    raise ValueError(f"Invalid environment configuration: {exc}") from exc

APP_ENV = settings.app_env.value
PORT = settings.port
DATABASE_URL = settings.database_url
REDIS_URL = settings.redis_url
LOG_LEVEL = settings.log_level.value
JWT_SECRET = settings.jwt_secret
CORS_ORIGIN = settings.cors_origin
API_KEY_A = settings.api_key_a
API_KEY_B = settings.api_key_b