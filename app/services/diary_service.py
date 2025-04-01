from app.db.chat_repository import ChatRepository
from app.db.diary_dao import DiaryDao
from datetime import datetime
from app.services.user_service import UserService
from app.services.dify_client import DifyClient
from app.core.config import settings

DATE_RANGE = 7

class DiaryService:

    def __init__(self):
        self.diary_dao = DiaryDao()
        self.chat_dao = ChatRepository()
        self.user_service = UserService()
        self.dify_client = DifyClient(settings.DIFY_DIARY_API_KEY)

    async def check_diary(self, user_id: str):
        lastday = int(datetime.today().strftime("%Y%m%d")) - 1
        for i in range(DATE_RANGE):
            day_int = lastday - i
            exist_diary = await self.diary_dao.exist_diary_by_day(user_id, day_int)
            # exist_message = await self.chat_dao.exist_messages(user_id, day_int)
            if exist_diary > 0:
                # 倒序检查，某一天存在，则前一天不再check
                return
            # elif exist_message == 0:
            #     # 不存在对话，跳过
            #     continue
            else:
                await self.create_diary_day(user_id, day_int)

    async def create_diary_day(self, user_id: str, day: int) -> str:
        print(f"开始处理日记，user_id: {user_id}")
        user_info = await self.user_service.get_user(user_id)
        print(f"获取到用户信息: {user_info}")
        if not user_info:
            print("未找到用户信息")
            raise ValueError("User not found")

        # todo difu yet
        chat_list = await self.chat_dao.get_messages_by_day(user_id, day)
        print("chat_list--: ", chat_list)
        response = await self.dify_client.get_diary(
            user_name=user_info.userNickName,
            user_id=user_info.userId,
            chat_list=chat_list,
        )
        print(f"Dify 响应: {response}")
        answer = response.get("answer", "")
        print(f"获取到回答: {answer}")

        await self.diary_dao.create_diary(user_id, answer, day)

    async def get_diary_summary(self, user_id: str, start: int, end: int) -> []:
        await self.check_diary(user_id)
        diarys = await self.diary_dao.get_diary_by_day_range(user_id, start, end)

        return diarys
