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
    agentId: Optional[str] = None  # Add this field

class GetUserStatusRequest(BaseModel):
    userId: str

class GetUserGrowthRequest(BaseModel):
    userId: str

# Database Models
class UserInfo(BaseModel):
    userId: str
    userNickName: str
    aiAgentName: str
    agentId: Optional[str] = None  # MemoBase 用户 ID
    status: UserStatus = UserStatus.LOGIN
    lastUpdateTime: str
    createdTime: int  # 毫秒级时间戳，表示用户创建时间
    
    def __init__(self, **data):
        print(f"正在创建 UserInfo 对象，输入数据: {data}")
        super().__init__(**data)
        print(f"UserInfo 对象创建完成: {self.dict()}")

class UserGrowth(BaseModel):
    userId: str
    currentPoints: int
    totalPoints: int = 1000
    lastUpdateTime: str

class UserTask(BaseModel):
    userId: str
    taskType: TaskType
    taskName: str
    requiredProgress: int
    pointsReward: int
    progress: int
    isCompleted: bool
    pointsClaimed: bool = False  # 添加积分领取状态
    lastUpdateTime: str

# Response Models
class GetUserStatusResponse(BaseModel):
    userInfo: UserInfo
    userGrowth: UserGrowth
    totalGrowthDays: int  # 添加总成长天数字段

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
