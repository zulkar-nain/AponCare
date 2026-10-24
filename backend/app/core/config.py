from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://aponcare:change-me@localhost:5432/aponcare"
    migration_database_url: str = "postgresql+asyncpg://aponcare:change-me@localhost:5432/aponcare"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "replace-this-before-deploying"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    betterstack_source_token: str = ""
    betterstack_ingesting_host: str = "https://in.logs.betterstack.com"
    backend_cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
