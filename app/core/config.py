from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MEMOBASE_PROJECT_URL: str = "http://localhost:8019"
    MEMOBASE_PROJECT_TOKEN: str = "secret"
    LINGYIWANWU_API_KEY: str = "a25cc7a127964db28793dfaf724debc8"
    LINGYIWANWU_API_BASE: str = "https://api.lingyiwanwu.com/v1"
    DIFY_API_BASE_URL: str = "https://api.dify.ai/v1"
    DIFY_API_KEY: str = "app-WVujRYUcFvvyyncgVcRs3au7"

    class Config:
        env_file = ".env"

settings = Settings()