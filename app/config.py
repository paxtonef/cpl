from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field(default="development")
    database_url: PostgresDsn
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_echo: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Runner placeholders for future phases — not used in B1
    vir_endpoint: str | None = Field(default=None)
    pgdr_endpoint: str | None = Field(default=None)
    vir_timeout: int = Field(default=30)
    pgdr_timeout: int = Field(default=60)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
