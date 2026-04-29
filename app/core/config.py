from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    secret_key: str
    algorithm: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()