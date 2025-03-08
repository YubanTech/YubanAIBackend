from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls, uri: str = "mongodb://localhost:27017"):
        try:
            logger.debug(f"Attempting to connect to MongoDB at {uri}")
            cls.client = AsyncIOMotorClient(uri)
            # 测试连接
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
            
    @classmethod
    async def close_db(cls):
        if cls.client:
            logger.debug("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")
            
    @classmethod
    def get_collection(cls, collection_name: str):
        if not cls.client:
            logger.error("MongoDB client not initialized. Call connect_db() first.")
            raise Exception("MongoDB client not initialized")
        logger.debug(f"Getting collection: {collection_name}")
        return cls.client.talk_to_myself[collection_name]
