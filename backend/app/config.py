from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: str = "devkey"
    livekit_api_secret: str = "secret"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql://voicd:voicd@localhost:5432/voicd"
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": "../.env", "extra": "ignore"}


settings = Settings()
