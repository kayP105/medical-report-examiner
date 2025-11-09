from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""

    APP_NAME: str = "Medical Report Explainer"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    
  
    LLM_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 500
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
