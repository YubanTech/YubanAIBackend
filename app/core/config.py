from pydantic_settings import BaseSettings
import os
# 微信小程序配置
WX_APPID = os.getenv("WX_APPID", "wx86ab8c9cb936067c")
WX_SECRET = os.getenv("WX_SECRET", "fb90299a4f66bba528809f4f8f3065d8")

class Settings(BaseSettings):
    # MongoDB 配置
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "yubanai")
    
    LINGYIWANWU_API_KEY: str = "a25cc7a127964db28793dfaf724debc8"
    LINGYIWANWU_API_BASE: str = "https://api.lingyiwanwu.com/v1"
    DIFY_API_BASE_URL: str = "https://api.dify.ai/v1"
    DIFY_API_KEY: str = "app-WVujRYUcFvvyyncgVcRs3au7"


    class Config:
        env_file = ".env"

settings = Settings()