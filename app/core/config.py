from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Información de la aplicación
    APP_NAME: str = "siscom-api"
    APP_VERSION: str = "0.1.0"

    # Configuración de Base de Datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_MIN_CONNECTIONS: int = 10
    DB_MAX_CONNECTIONS: int = 20
    DB_CONNECTION_TIMEOUT_SECS: int = 30
    DB_IDLE_TIMEOUT_SECS: int = 300

    # Seguridad JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS (opcional)
    ALLOWED_ORIGINS: str = "*"

    # Para compatibilidad con código existente que use DATABASE_URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    class Config:
        env_file = ".env"


settings = Settings()
