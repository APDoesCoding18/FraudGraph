from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FraudGraph API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraudgraph"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TRANSACTION_TOPIC: str = "transaction-events"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # LLM (Ollama via OpenAI SDK)
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"
    OLLAMA_MODEL: str = "llama3"
    
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_ignore_empty=True, extra="ignore")

settings = Settings()
