from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pytz

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def get_chat_messages(cls, user_id: str, date: datetime, page: int, page_size: int) -> List[Dict[str, Any]]:
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        start = shanghai_tz.localize(datetime(date.year, date.month, date.day)).astimezone(pytz.utc)
        end = start + timedelta(days=1)
        
        collection = cls.get_collection("chat_messages")
        cursor = collection.find({
            "userId": user_id,
            "timestamp": {
                "$gte": start,
                "$lt": end
            }
        }).skip(page * page_size).limit(page_size)
        return await cursor.to_list(length=page_size)

    async def connect_db(cls):
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        
    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            
    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.client.talk_to_myself[collection_name]

    @classmethod
    async def insert_chat_message(cls, chat_message: Dict[str, Any]):
        collection = cls.get_collection("chat_messages")
        result = await collection.insert_one(chat_message)
        return result.inserted_id

    @classmethod
    async def store_daily_summary(cls, user_id: str, summary_date: datetime, summary_content: str):
        collection = cls.get_collection("daily_summaries")
        summary = {
            "userId": user_id,
            "summary_date": summary_date,
            "content": summary_content,
            "created_at": datetime.now()
        }
        result = await collection.insert_one(summary)
        return result.inserted_id

    @classmethod
    async def get_chat_messages(cls, user_id: str, start_time: datetime, end_time: datetime, page: int, page_size: int) -> List[Dict[str, Any]]:
        collection = cls.get_collection("chat_messages")
        cursor = collection.find({
            "userId": user_id,
            "timestamp": {
                "$gte": start_time,
                "$lt": end_time
            }
        }).skip(page * page_size).limit(page_size)
        return await cursor.to_list(length=page_size)
