from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Travel Planner"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://travel:travel_dev_2026@localhost:5432/ai_travel"
    redis_url: str = "redis://localhost:6379"

    # LLM
    llm_api_key: str = "sk-placeholder"
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"

    # MVP City
    mvp_city: str = "chongqing"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
