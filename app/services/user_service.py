from datetime import datetime
from app.database.mongodb import MongoDB
from app.models.user import CreateUserRequest, UserInfo, UserStatus

class UserService:
    @staticmethod
    async def create_user(user_request: CreateUserRequest) -> None:
        user_collection = MongoDB.get_collection("users")
        
        # 检查用户是否已存在
        existing_user = await user_collection.find_one({"userId": user_request.userId})
        if existing_user:
            return None
            
        # 创建新用户
        user_info = UserInfo(
            userId=user_request.userId,
            userNickName=user_request.userNickName,
            aiAgentName=user_request.aiAgentName,
            status=UserStatus.LOGIN,
            lastUpdateTime=datetime.now().isoformat()
        )
        
        await user_collection.insert_one(user_info.dict())
