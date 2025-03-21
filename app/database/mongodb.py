from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db_name: str = "yubanai"  # Add default database name
    
    @classmethod
    async def connect_db(cls, mongo_uri: str):
        try:
            logger.debug(f"Attempting to connect to MongoDB at {mongo_uri}")
            cls.client = AsyncIOMotorClient(
                mongo_uri,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                maxPoolSize=10,
                retryWrites=True
            )
            # Wait for connection to be ready
            await cls.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {mongo_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
            
    @classmethod
    def get_collection(cls, collection_name: str):
        if not cls.client:
            logger.error("MongoDB client not initialized. Call connect_db() first.")
            raise Exception("MongoDB client not initialized")
        logger.debug(f"Getting collection: {collection_name}")
        return cls.client[cls.db_name][collection_name]  # Use db_name instead of hardcoded database
