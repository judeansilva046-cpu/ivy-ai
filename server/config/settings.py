"""
Configuration module for Ivy AI
Uses Pydantic Settings to load environment variables
Evolved from Jarvis AI with enhanced agent architecture
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Ivy AI - Intelligent Versatile Assistant"
    APP_VERSION: str = "2.0.0-ivy"
    DEBUG: bool = False

    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "jarvis_db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Qdrant Vector Database
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "jarvis_knowledge"
    QDRANT_VECTOR_SIZE: int = 1536  # OpenAI embedding dimension

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_CHAT: str = "gpt-3.5-turbo"
    OPENAI_MODEL_EMBEDDINGS: str = "text-embedding-3-small"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2048

    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "jarvis-documents"

    # RAG Settings
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5
    RAG_MIN_SCORE: float = 0.5

    # Document paths (using absolute paths)
    DOCUMENTS_PATH: str = "C:\\JarvisAI\\documents"
    UPLOADS_PATH: str = "C:\\JarvisAI\\server\\uploads"
    LOGS_PATH: str = "C:\\JarvisAI\\server\\logs"
    DATA_PATH: str = "C:\\JarvisAI\\server\\data"

    # N8N Integration
    N8N_URL: Optional[str] = "http://localhost:5678"
    N8N_API_KEY: Optional[str] = None
    N8N_LICENSE_ACTIVATION_KEY: Optional[str] = None
    N8N_ENCRYPTION_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Timezone
    TZ: str = "America/Sao_Paulo"
    GENERIC_TIMEZONE: str = "America/Sao_Paulo"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignora variáveis extras


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
