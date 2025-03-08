from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    user_id: str
    role: str  # system/user/assistant
    content: str
    created_at: datetime = datetime.now()
    agent_name: Optional[str] = None