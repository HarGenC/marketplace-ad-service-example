from pydantic import PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    _database_url: str | None = PrivateAttr(default=None)
    postgres_database_name: str = "ads_db"
    postgres_host: str = "ad-postgres"
    postgres_port: str = "5432"
    postgres_username: str = "postgres"
    postgres_password: str = "postgres"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    kafka_bootstrap_servers: str = "ad-redpanda:9092"
    kafka_topic_ads: str = "ads"
    auth_service_url: str = "http://localhost:8000"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_username}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database_name}"
        )
