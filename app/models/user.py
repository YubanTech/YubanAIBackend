from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserStatus(str, Enum):
    LOGIN = "LOGIN"
    CHAT_READY = "CHAT_READY"

class CreateUserRequest(BaseModel):
    userId: str
    userNickName: str
    aiAgentName: str

class UserInfo(BaseModel):
    userId: str
    userNickName: str
    aiAgentName: str
    agentId: Optional[str] = None
    status: UserStatus = UserStatus.LOGIN
    lastUpdateTime: str
