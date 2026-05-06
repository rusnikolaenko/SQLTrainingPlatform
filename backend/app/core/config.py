from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    trainer_db_url: str = (
        "postgresql+asyncpg://trainer_user:trainer_pass@localhost:5433/trainer"
    )
    sandbox_db_url: str = (
        "postgresql+asyncpg://postgres:sandbox_pass@localhost:5434/sandbox"
    )
    # DSN for sandbox_user — the restricted role used to execute user queries
    sandbox_user_dsn: str = (
        "postgresql://sandbox_user:sandbox_user_pass@localhost:5434/sandbox"
    )

    @property
    def sandbox_asyncpg_dsn(self) -> str:
        return self.sandbox_db_url.replace("postgresql+asyncpg://", "postgresql://")


settings = Settings()
