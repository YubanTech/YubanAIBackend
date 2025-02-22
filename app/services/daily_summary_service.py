from .scheduler_service import SchedulerService
from .mongodb import MongoDB
import pytz
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import os

class DailySummaryService(SchedulerService):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.env = Environment(loader=FileSystemLoader('app/prompts'))
        self._init_scheduler()
        
    def _init_scheduler(self) -> None:
        """Initialize scheduler with daily job at 6AM Beijing time"""
        try:
            self.add_job(
                self.generate_summary,
                'cron',
                hour=6,
                timezone=pytz.timezone('Asia/Shanghai'),
                args=["system_auto"],
                misfire_grace_time=300
            )
        except Exception as e:
            raise RuntimeError(f"Scheduler initialization failed: {str(e)}")
    
    @staticmethod
    def _get_prompt_template() -> str:
        """Return the Jinja2 template for daily summaries."""
        return """
        今日聊天主题：{{ main_topics | join(', ') }}
        情感分析：{{ sentiment_analysis }}
        """
        
    async def generate_summary(self, user_id: str = "system_auto"):
        if not user_id or user_id.strip() == "":
            raise ValueError("用户ID不能为空")
            
        # 空记录处理
        from datetime import datetime, timedelta, date, time
        from pytz import timezone

        shanghai_tz = timezone('Asia/Shanghai')
        start_time = shanghai_tz.localize(datetime.combine(date.today(), time(0, 0)))
        end_time = start_time + timedelta(hours=6)

        messages = await MongoDB.get_chat_messages(user_id, start_time, end_time)
        if not messages:
            return "今天还没有和我聊天哦，快来和我聊聊吧！(๑•̀ㅂ•́)و✧"
        template = self.env.get_template('daily_summary.jinja2')
        VALID_MSG_TYPES = {'user', 'group', 'system'}
        filtered_messages = [
            msg for msg in messages 
            if msg['type'] in VALID_MSG_TYPES 
            and not msg.get('is_system_generated')
        ]

        prompt = template.render(user_name=user_id, messages=filtered_messages)
        
        from tenacity import retry, stop_after_attempt

        @retry(stop=stop_after_attempt(3))
        async def save_summary_to_db(user_id, content):
            async with MongoDB.client.start_session() as session:
                async with session.start_transaction():
                    # 存储逻辑
                    pass

        response = await self.client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        
        return response.choices[0].text.strip()
