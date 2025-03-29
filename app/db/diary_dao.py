from app.models.user import UserInfo
from app.database.mongodb import MongoDB
from datetime import datetime
from app.models.diary import Diary

class DiaryDao:
    def __init__(self):
        self.collection = MongoDB.get_collection("diary")

    async def create_diary(self, user_id: str, diary_content: str, date_int: int):
        date_obj = datetime.strptime(str(date_int), "%Y%m%d")
        diary = Diary(
            user_id=user_id,
            diary=diary_content,
            date_int=date_int,
            date=date_obj.strftime("%Y年%m月%d日")
        )
        await self.collection.insert_one(diary.model_dump())

    async def exist_diary_by_day(self, user_id: str, date_int: int):
        exist = await self.collection.count_documents({"user_id": user_id, "date_int": date_int}, limit=1)
        return exist

    async def get_diary_by_day_range(self, user_id: str, start: int, end: int) -> []:
        cursor = self.collection.find({
            "user_id": user_id,
            "date_int": {
                "$gte": start,
                "$lte": end
            }
        }).sort("date_int", 1)

        messages = []
        async for doc in cursor:
            messages.append(Diary(**doc))
        return messages
