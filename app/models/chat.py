from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatMessage(BaseModel):
    user_id: str
    role: str
    content: str
    # used for index
    date_int: int = int(datetime.today().strftime("%Y%m%d"))
    agent_name: str
    created_at: str = datetime.now().isoformat()  # 改为 created_at

class ChatHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryItem]
    total: int
    current_page: int
