from app.models.user import UserInfo
from app.database.mongodb import MongoDB
from datetime import datetime
from app.models.diary import Diary

class DiaryDao:
    def __init__(self):
        self.collection = MongoDB.get_collection("diary")

    async def create_diary(self, user_id: str, diary_content: str):
        diary = Diary(
            user_id=user_id,
            diary=diary_content,
        )
        await self.collection.update_one(
            {"user_id": user_id, "date_index": diary.date_index},
            {"$set": diary.model_dump()},
            upsert=True
        )

    async def exist_diary_by_day(self, user_id: str, day: int):
        exist = await self.collection.count_documents({"user_id": user_id, "day": day}, limit=1)
        return exist

    async def get_diary_by_day_range(self, user_id: str, start: int, end: int) -> []:
        cursor = self.collection.find({
            "user_id": user_id,
            "date_index": {
                "$gte": start,
                "$lte": end
            }
        }).sort("date_index", 1)

        messages = []
        async for doc in cursor:
            messages.append(Diary(**doc))
        return messages
