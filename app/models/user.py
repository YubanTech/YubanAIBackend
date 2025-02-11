from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class UserStatus(str, Enum):
    LOGIN = "LOGIN"
    CHAT_READY = "CHAT_READY"

class TaskType(str, Enum):
    CHAT_ROUNDS = "CHAT_ROUNDS"
    FORTUNE_TELLING = "FORTUNE_TELLING"
    DAILY_CHECK_IN = "DAILY_CHECK_IN"

# Request/Response Models
class CreateUserRequest(BaseModel):
    userId: str
    userNickName: str
    aiAgentName: str

class UpdateUserRequest(BaseModel):
    userNickName: str
    aiAgentName: str

class GetUserStatusRequest(BaseModel):
    userId: str

class GetUserGrowthRequest(BaseModel):
    userId: str

# Database Models
class UserInfo(BaseModel):
    userId: str
    userNickName: str
    aiAgentName: str
    agentId: Optional[str] = None
    status: UserStatus = UserStatus.LOGIN
    lastUpdateTime: str

class UserGrowth(BaseModel):
    userId: str
    currentPoints: int
    totalPoints: int = 1000
    lastUpdateTime: str

class UserTask(BaseModel):
    userId: str
    taskType: TaskType
    progress: int
    isCompleted: bool
    lastUpdateTime: str

# Response Models
class GetUserStatusResponse(BaseModel):
    userInfo: UserInfo
    userGrowth: UserGrowth

class GetUserGrowthResponse(BaseModel):
    userGrowth: UserGrowth
    tasks: List[UserTask]

# Constants
class GrowthTask(BaseModel):
    type: str
    name: str
    requiredProgress: int
    pointsReward: int

class GrowthTasks:
    CHAT_ROUNDS = GrowthTask(
        type="CHAT_ROUNDS",
        name="与智能体开展20轮对话",
        requiredProgress=20,
        pointsReward=50
    )
    FORTUNE_TELLING = GrowthTask(
        type="FORTUNE_TELLING",
        name="开启一次占星",
        requiredProgress=1,
        pointsReward=50
    )
    DAILY_CHECK_IN = GrowthTask(
        type="DAILY_CHECK_IN",
        name="打卡一次",
        requiredProgress=1,
        pointsReward=50
    )

    @classmethod
    def get_all_tasks(cls) -> dict:
        return {
            "CHAT_ROUNDS": cls.CHAT_ROUNDS,
            "FORTUNE_TELLING": cls.FORTUNE_TELLING,
            "DAILY_CHECK_IN": cls.DAILY_CHECK_IN
        }
