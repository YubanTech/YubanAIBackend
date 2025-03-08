from datetime import datetime, time
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database.mongodb import MongoDB
from app.models.user import (
    CreateUserRequest, UpdateUserRequest, UserInfo, UserGrowth, 
    UserTask, TaskType, UserStatus, GrowthTasks
)
from app.models.db_models import user_info_to_dict, user_growth_to_dict, user_task_to_dict

class UserService:
    @staticmethod
    def _process_mongodb_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
        if doc is None:
            return None
        
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    @staticmethod
    async def create_user(user_request: CreateUserRequest) -> None:
        user_collection = MongoDB.get_collection("users")
        growth_collection = MongoDB.get_collection("user_growth")
        task_collection = MongoDB.get_collection("user_tasks")
        
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
        
        # 创建用户成长信息
        user_growth = UserGrowth(
            userId=user_request.userId,
            currentPoints=0,
            totalPoints=1000,
            lastUpdateTime=datetime.now().isoformat()
        )
        
        # 创建用户任务
        tasks = []
        for task in GrowthTasks.get_all_tasks().values():
            user_task = UserTask(
                userId=user_request.userId,
                taskType=task.type,
                progress=0,
                isCompleted=False,
                lastUpdateTime=datetime.now().isoformat()
            )
            tasks.append(user_task_to_dict(user_task))
        
        # 保存到数据库
        await user_collection.insert_one(user_info_to_dict(user_info))
        await growth_collection.insert_one(user_growth_to_dict(user_growth))
        await task_collection.insert_many(tasks)
        
    @staticmethod
    async def update_user(userId: str, update_request: UpdateUserRequest) -> None:
        user_collection = MongoDB.get_collection("users")
        
        print(f"更新用户请求数据: {update_request}")  # 添加调试信息
        
        update_data = {
            "userNickName": update_request.userNickName,
            "aiAgentName": update_request.aiAgentName,
            "lastUpdateTime": datetime.now().isoformat()
        }
        
        # 检查 agentId
        if hasattr(update_request, 'agentId') and update_request.agentId:
            print(f"更新 agentId: {update_request.agentId}")  # 添加调试信息
            update_data["agentId"] = update_request.agentId
        
        print(f"最终更新数据: {update_data}")  # 添加调试信息
        
        result = await user_collection.update_one(
            {"userId": userId},
            {"$set": update_data}
        )
        print(f"更新结果: matched={result.matched_count}, modified={result.modified_count}")  # 添加调试信息
        
    @staticmethod
    async def get_user_status(userId: str) -> Optional[dict]:
        user_collection = MongoDB.get_collection("users")
        growth_collection = MongoDB.get_collection("user_growth")
        
        user_info = await user_collection.find_one({"userId": userId})
        user_growth = await growth_collection.find_one({"userId": userId})
        
        if not user_info or not user_growth:
            return None
            
        return {
            "userInfo": UserService._process_mongodb_doc(user_info),
            "userGrowth": UserService._process_mongodb_doc(user_growth)
        }
        
    @staticmethod
    def _get_today_start() -> datetime:
        """获取今天0点的时间"""
        today = datetime.now()
        return datetime.combine(today.date(), time.min)

    @staticmethod
    def _should_reset_daily_task(task: Dict[str, Any]) -> bool:
        """判断每日任务是否需要重置"""
        if task["taskType"] != TaskType.DAILY_CHECK_IN:
            return False
        
        last_update = datetime.fromisoformat(task["lastUpdateTime"])
        today_start = UserService._get_today_start()
        return last_update < today_start

    @staticmethod
    async def get_user_growth(userId: str) -> Optional[dict]:
        growth_collection = MongoDB.get_collection("user_growth")
        task_collection = MongoDB.get_collection("user_tasks")
        
        user_growth = await growth_collection.find_one({"userId": userId})
        if not user_growth:
            return None
            
        tasks = []
        async for task in task_collection.find({"userId": userId}):
            processed_task = UserService._process_mongodb_doc(task)
            
            # 检查每日任务是否需要重置
            if UserService._should_reset_daily_task(processed_task):
                # 更新任务状态为未完成
                await task_collection.update_one(
                    {"userId": userId, "taskType": TaskType.DAILY_CHECK_IN},
                    {
                        "$set": {
                            "isCompleted": False,
                            "progress": 0
                        }
                    }
                )
                processed_task["isCompleted"] = False
                processed_task["progress"] = 0
                
            tasks.append(processed_task)
            
        return {
            "userGrowth": UserService._process_mongodb_doc(user_growth),
            "tasks": tasks
        }

    @staticmethod
    async def update_user_growth(userId: str, taskType: TaskType) -> Optional[dict]:
        growth_collection = MongoDB.get_collection("user_growth")
        task_collection = MongoDB.get_collection("user_tasks")
        
        # 获取任务信息
        task_config = GrowthTasks.get_all_tasks().get(taskType)
        if not task_config:
            return None
            
        # 获取用户当前任务进度
        user_task = await task_collection.find_one({
            "userId": userId,
            "taskType": taskType
        })
        
        if not user_task:
            return None
            
        # 处理每日任务的特殊逻辑
        if taskType == TaskType.DAILY_CHECK_IN:
            if UserService._should_reset_daily_task(user_task):
                # 如果是新的一天，重置任务状态
                user_task["isCompleted"] = False
                user_task["progress"] = 0
            elif user_task["isCompleted"]:
                # 如果是同一天且已完成，则不能重复完成
                return None
        else:
            # 非每日任务，如果已完成则不能重复完成
            if user_task["isCompleted"]:
                return None
            
        # 更新任务进度
        new_progress = min(user_task["progress"] + 1, task_config.requiredProgress)
        is_completed = new_progress >= task_config.requiredProgress
        
        await task_collection.update_one(
            {"userId": userId, "taskType": taskType},
            {
                "$set": {
                    "progress": new_progress,
                    "isCompleted": is_completed,
                    "lastUpdateTime": datetime.now().isoformat()
                }
            }
        )
        
        # 如果任务完成，增加成长值
        if is_completed:
            await growth_collection.update_one(
                {"userId": userId},
                {
                    "$inc": {"currentPoints": task_config.pointsReward},
                    "$set": {"lastUpdateTime": datetime.now().isoformat()}
                }
            )
            
        # 返回更新后的用户成长信息
        return await UserService.get_user_growth(userId)

    @staticmethod
    async def get_user(userId: str) -> Optional[UserInfo]:
        user_collection = MongoDB.get_collection("users")
        
        user_doc = await user_collection.find_one({"userId": userId})
        if not user_doc:
            return None
            
        # 处理 MongoDB 文档
        processed_doc = UserService._process_mongodb_doc(user_doc)
        
        # 转换为 UserInfo 对象
        return UserInfo(
            userId=processed_doc["userId"],
            userNickName=processed_doc.get("userNickName", ""),
            aiAgentName=processed_doc.get("aiAgentName", "小月"),
            status=UserStatus(processed_doc.get("status", UserStatus.LOGIN.value)),
            lastUpdateTime=processed_doc.get("lastUpdateTime", datetime.now().isoformat()),
            agentId=processed_doc.get("agentId")
        )
