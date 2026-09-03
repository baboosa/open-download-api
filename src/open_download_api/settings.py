from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    redis_host: str = "localhost"
    redis_port: int = 6379
    job_store_redis_db: int = 1
    celery_broker_db: int = 0

settings = Settings()