from app.db.chat_repository import ChatRepository
from app.db.diary_dao import DiaryDao
from app.models.user import UserInfo
from datetime import datetime

DATE_RANGE = 7

class DiaryService:

    def __init__(self):
        self.diary_dao = DiaryDao()
        self.chat_dao = ChatRepository()

    async def check_diary(self, user_id: str):
        lastday = int(datetime.today().strftime("%Y%m%d")) - 1
        for i in range(DATE_RANGE):
            day_int = lastday - i
            exist_diary = await self.diary_dao.exist_diary_by_day(user_id, day_int)
            exist_message = await self.chat_dao.exist_messages(user_id, day_int)
            print("exist_check ---------> ", exist_diary, exist_message, day_int)
            if exist_diary > 0:
                # 倒序检查，某一天存在，则前一天不再check
                return
            elif exist_message == 0:
                # 不存在对话，跳过
                continue
            else:
                await self.create_diary_day(user_id, day_int)

    async def create_diary_day(self, user_id: str, day: int) -> str:
        # todo difu yet
        diary = "这是一条测试日记，等待dify完成后接入"
        await self.diary_dao.create_diary(user_id, diary, day)

        return diary

    async def get_diary_summary(self, user_id: str, start: int, end: int) -> []:
        await self.check_diary(user_id)
        diarys = await self.diary_dao.get_diary_by_day_range(user_id, start, end)

        return diarys
