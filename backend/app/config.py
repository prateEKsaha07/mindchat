from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = True

    # JWT settings
    SECRET_KEY: str = "travel-makes-me-happy"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    #model settings
    MODEL_PATH: str = "D:/mindchat/model/checkpoints/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    MODEL_MAX_TOKENS: int = 512
    MODEL_TEMPERATURE: float = 0.7
    MODEL_CONTEXT_LENGTH: int = 2048

    class Config:
        env_file = ".env"
    
settings = Settings()