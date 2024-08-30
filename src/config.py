from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # database related
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    DATABASE_URL: str
    
    # JWT Token Related
    secret_key: str
    refresh_secret_key : str
    algorithm: str
    timeout: int
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_MINUTES : int

    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_PORT: int
    EMAIL_SERVER: str
    EMAIL_TLS: bool
    EMAIL_SSL: bool

    RESET_PASSWORD_URL: str
    APP_HOST: str

    class Config:
        env_file = Path(Path(__file__).resolve().parent) / ".env"
        print(f'environment created - {Path(Path(__file__).resolve().name)}')

setting = Settings()
