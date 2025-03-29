from datetime import datetime
from typing import List
from app.models.chat import ChatMessage
from app.database.mongodb import MongoDB

class ChatRepository:
    def __init__(self):
        self.collection = MongoDB.get_collection("chat_messages")

    async def save_message(self, message: ChatMessage):
        await self.collection.insert_one(message.dict())

    async def get_messages_by_day(self, user_id: str, date_int: int) -> List[ChatMessage]:
        cursor = self.collection.find({
            "user_id": user_id,
            "date_int": date_int
        }).sort("created_at", 1)

        messages = []
        async for doc in cursor:
            messages.append(ChatMessage(**doc))
        return messages

    async def exist_messages(self, user_id: str, date_int: int) -> int:
        exist = await self.collection.count_documents({"user_id": user_id, "date_int": date_int}, limit=1)
        return exist

    async def get_messages_by_time_range(
        self, 
        user_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[ChatMessage]:
        cursor = self.collection.find({
            "user_id": user_id,
            "created_at": {
                "$gte": start_time,
                "$lte": end_time
            }
        }).sort("created_at", 1)
        
        messages = []
        async for doc in cursor:
            messages.append(ChatMessage(**doc))
        return messages