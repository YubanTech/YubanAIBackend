from datetime import datetime, time, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
import logging  # 添加logging导入
import time
import math
import requests
import uuid
# 添加这两行
WX_APPID = "wx86ab8c9cb936067c"
WX_SECRET = "fb90299a4f66bba528809f4f8f3065d8"
# 定义logger
logger = logging.getLogger(__name__)

from app.database.mongodb import MongoDB
from app.models.user import (
    CreateUserRequest, UpdateUserRequest, UserInfo, UserGrowth, 
    UserTask, TaskType, UserStatus, GrowthTasks, WxLoginRequest
)
from app.models.db_models import user_info_to_dict, user_growth_to_dict, user_task_to_dict

# 添加微信登录相关常量
WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

class UserService:
    @staticmethod
    def calculate_growth_days(created_time_ms: int) -> int:
        """
        计算用户的总成长天数
        
        Args:
            created_time_ms: 用户创建时间的毫秒时间戳
            
        Returns:
            int: 用户注册至今的总天数（向上取整）
        """
        try:
            # 获取当前时间的毫秒时间戳
            current_time_ms = int(time.time() * 1000)
            
            # 计算时间差（毫秒）
            time_diff_ms = current_time_ms - created_time_ms
            
            # 转换为天数（1天 = 86400000毫秒）
            days = time_diff_ms / 86400000
            
            # 向上取整
            days_rounded = math.ceil(days)
                
            return max(1, days_rounded)  # 至少返回1天
        except Exception as e:
            logger.error(f"Error calculating growth days: {str(e)}")
            return 1  # 出错时默认返回1天

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
        logger.info(f"Creating user: {user_request}")
        user_collection = MongoDB.get_collection("users")
        growth_collection = MongoDB.get_collection("user_growth")
        task_collection = MongoDB.get_collection("user_tasks")
        
        # 检查用户是否已存在
        existing_user = await user_collection.find_one({"userId": user_request.userId})
        if existing_user:
            logger.info(f"User already exists: {existing_user}")
            return None
        
        # 获取当前时间
        current_time = datetime.now().isoformat()
        # 获取当前毫秒时间戳
        current_ms_timestamp = int(time.time() * 1000)
        
        # 创建新用户
        user_info = UserInfo(
            userId=user_request.userId,
            userNickName=user_request.userNickName,
            aiAgentName=user_request.aiAgentName,
            agentId=None,
            status=UserStatus.CHAT_READY,
            lastUpdateTime=current_time,
            createdTime=current_ms_timestamp  # 使用毫秒时间戳
        )
        
        # 创建用户成长信息
        user_growth = UserGrowth(
            userId=user_request.userId,
            currentPoints=0,
            totalPoints=1000,
            lastUpdateTime=current_time
        )
        
        # 创建用户任务
        tasks = []
        for task_config in GrowthTasks.get_all_tasks().values():
            user_task = UserTask(
                userId=user_request.userId,
                taskType=task_config.type,
                taskName=task_config.name,           # 添加任务名称
                requiredProgress=task_config.requiredProgress,  # 添加所需进度
                pointsReward=task_config.pointsReward,  # 添加奖励点数
                progress=0,
                isCompleted=False,
                lastUpdateTime=current_time
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
        logger.info(f"Getting user status for user: {userId}")
        user_collection = MongoDB.get_collection("users")
        growth_collection = MongoDB.get_collection("user_growth")
        
        user_info = await user_collection.find_one({"userId": userId})
        user_growth = await growth_collection.find_one({"userId": userId})
        
        if not user_info or not user_growth:
            return None
        
        # 处理文档
        processed_user_info = UserService._process_mongodb_doc(user_info)
        processed_user_growth = UserService._process_mongodb_doc(user_growth)
        
        # 计算总成长天数
        # 如果用户没有createdTime字段，使用当前时间作为默认值
        created_time_ms = processed_user_info.get("createdTime", int(time.time() * 1000))
        total_growth_days = UserService.calculate_growth_days(created_time_ms)
        logger.info(f"User {userId} has been growing for {total_growth_days} days")
        
        # 构造用户信息和成长信息对象
        user_info_obj = UserInfo(
            userId=processed_user_info["userId"],
            userNickName=processed_user_info.get("userNickName", ""),
            aiAgentName=processed_user_info.get("aiAgentName", ""),
            agentId=processed_user_info.get("agentId"),
            status=processed_user_info.get("status", UserStatus.LOGIN),
            lastUpdateTime=processed_user_info.get("lastUpdateTime", ""),
            createdTime=created_time_ms
        )
        
        user_growth_obj = UserGrowth(
            userId=processed_user_growth["userId"],
            currentPoints=processed_user_growth.get("currentPoints", 0),
            totalPoints=processed_user_growth.get("totalPoints", 1000),
            lastUpdateTime=processed_user_growth.get("lastUpdateTime", "")
        )
            
        return {
            "userInfo": user_info_obj,
            "userGrowth": user_growth_obj,
            "totalGrowthDays": total_growth_days
        }
        
    @staticmethod
    def _get_today_start() -> datetime:
        """获取今天0点的时间"""
        today = datetime.now()
        return datetime.combine(today.date(), datetime.min.time())

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
        print(f"开始获取用户成长信息，userId: {userId}")
        growth_collection = MongoDB.get_collection("user_growth")
        task_collection = MongoDB.get_collection("user_tasks")
        
        user_growth = await growth_collection.find_one({"userId": userId})
        print(f"用户成长信息: {user_growth}")
        if not user_growth:
            print("未找到用户成长信息")
            return None
            
        tasks = []
        all_task_configs = GrowthTasks.get_all_tasks()
        print(f"所有任务配置: {all_task_configs}")
        
        async for task in task_collection.find({"userId": userId}):
            print(f"处理任务: {task}")
            processed_task = UserService._process_mongodb_doc(task)
            task_config = all_task_configs.get(processed_task["taskType"])
            
            if task_config:
                processed_task.update({
                    "taskName": task_config.name,
                    "requiredProgress": task_config.requiredProgress,
                    "pointsReward": task_config.pointsReward,
                    "pointsClaimed": processed_task.get("pointsClaimed", False)  # 确保返回积分领取状态
                })
            
            tasks.append(processed_task)
            
        result = {
            "userGrowth": UserService._process_mongodb_doc(user_growth),
            "tasks": tasks
        }
        print(f"最终返回结果: {result}")
        return result

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
        
        # 对话类任务每次都增加积分，其他任务仅在完成时增加积分
        if taskType == TaskType.CHAT_ROUNDS or is_completed:
            # 如果是对话任务，每次进度更新都给予相应积分
            points_to_add = task_config.pointsReward
            await growth_collection.update_one(
                {"userId": userId},
                {
                    "$inc": {"currentPoints": points_to_add},
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
        
        # 获取当前时间戳作为默认值
        current_ms_timestamp = int(time.time() * 1000)
        
        # 转换为 UserInfo 对象
        return UserInfo(
            userId=processed_doc["userId"],
            userNickName=processed_doc.get("userNickName", ""),
            aiAgentName=processed_doc.get("aiAgentName", "小月"),
            status=UserStatus(processed_doc.get("status", UserStatus.LOGIN.value)),
            lastUpdateTime=processed_doc.get("lastUpdateTime", datetime.now().isoformat()),
            agentId=processed_doc.get("agentId"),
            createdTime=processed_doc.get("createdTime", current_ms_timestamp)  # 添加 createdTime 字段
        )

    @staticmethod
    async def login_with_wechat(login_request: WxLoginRequest) -> Optional[dict]:
        """
        处理微信小程序登录（简化版）
        """
        try:
            # 1. 调用微信API获取OpenID
            wx_response = requests.get(
                WX_CODE2SESSION_URL,
                params={
                    "appid": WX_APPID,
                    "secret": WX_SECRET,
                    "js_code": login_request.code,
                    "grant_type": "authorization_code"
                }
            )
            wx_data = wx_response.json()
            
            if "errcode" in wx_data and wx_data["errcode"] != 0:
                logger.error(f"微信登录失败: {wx_data}")
                return None
            
            openid = wx_data.get("openid")
            if not openid:
                logger.error("未能获取OpenID")
                return None
            
            # 2. 查询用户是否存在
            user_collection = MongoDB.get_collection("users")
            existing_user = await user_collection.find_one({"openId": openid})
            
            # 获取当前时间作为更新/创建时间
            current_time = datetime.now().isoformat()
            current_ms_timestamp = int(time.time() * 1000)
            
            # 3. 处理用户信息
            if existing_user:
                # 用户已存在，更新信息
                user_id = existing_user["userId"]
                logger.info(f"用户已存在，更新信息: {user_id}")
                
                # 更新用户信息
                await user_collection.update_one(
                    {"userId": user_id},
                    {"$set": {
                        "userNickName": login_request.nickName,
                        "avatarUrl": login_request.avatarUrl,
                        "lastUpdateTime": current_time
                    }}
                )
            else:
                # 创建新用户
                user_id = f"wxuser_{uuid.uuid4().hex[:8]}"
                logger.info(f"创建新用户: {user_id}")
                
                # 创建用户基本信息
                user_info = UserInfo(
                    userId=user_id,
                    userNickName=login_request.nickName,
                    aiAgentName="AI助手",  # 默认AI助手名称
                    status=UserStatus.CHAT_READY,
                    lastUpdateTime=current_time,
                    createdTime=current_ms_timestamp,
                    openId=openid,
                    avatarUrl=login_request.avatarUrl
                )
                
                # 创建用户成长信息
                user_growth = UserGrowth(
                    userId=user_id,
                    currentPoints=0,
                    totalPoints=1000,
                    lastUpdateTime=current_time
                )
                
                # 创建用户任务
                tasks = []
                for task in GrowthTasks.get_all_tasks().values():
                    user_task = UserTask(
                        userId=user_id,
                        taskType=task.type,
                        progress=0,
                        isCompleted=False,
                        lastUpdateTime=current_time
                    )
                    tasks.append(user_task_to_dict(user_task))
                
                # 保存到数据库
                await user_collection.insert_one(user_info_to_dict(user_info))
                await MongoDB.get_collection("user_growth").insert_one(user_growth_to_dict(user_growth))
                await MongoDB.get_collection("user_tasks").insert_many(tasks)
            
            # 5. 获取完整用户信息并返回
            user_status = await UserService.get_user_status(user_id)
            
            return user_status  # 直接返回用户状态信息
            
        except Exception as e:
            logger.error(f"微信登录处理错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    async def mark_task_completed(userId: str, taskType: TaskType) -> Optional[dict]:
        """标记任务为已完成状态"""
        task_collection = MongoDB.get_collection("user_tasks")
        
        # 获取任务配置
        task_config = GrowthTasks.get_all_tasks().get(taskType)
        if not task_config:
            return None
            
        # 获取当前任务状态
        task = await task_collection.find_one({
            "userId": userId,
            "taskType": taskType
        })
        
        if not task:
            return None
            
        if task.get("isCompleted", False):
            return None
            
        # 更新任务状态为已完成
        current_time = datetime.now().isoformat()
        result = await task_collection.update_one(
            {
                "userId": userId,
                "taskType": taskType
            },
            {
                "$set": {
                    "isCompleted": True,
                    "progress": task_config.requiredProgress,
                    "lastUpdateTime": current_time
                }
            }
        )
        
        if result.modified_count > 0:
            return {
                "taskType": taskType,
                "isCompleted": True,
                "progress": task_config.requiredProgress
            }
        return None

    @staticmethod
    async def claim_task_points(userId: str, taskType: TaskType) -> Optional[dict]:
        """领取已完成任务的积分"""
        task_collection = MongoDB.get_collection("user_tasks")
        growth_collection = MongoDB.get_collection("user_growth")
        
        # 获取任务配置
        task_config = GrowthTasks.get_all_tasks().get(taskType)
        if not task_config:
            return None
            
        # 获取任务状态
        task = await task_collection.find_one({
            "userId": userId,
            "taskType": taskType
        })
        
        # 检查任务是否已完成且未领取积分
        if not task or not task.get("isCompleted", False) or task.get("pointsClaimed", False):
            return None
            
        # 获取用户成长信息
        user_growth = await growth_collection.find_one({"userId": userId})
        if not user_growth:
            return None
            
        current_time = datetime.now().isoformat()
        
        # 更新用户积分
        new_current_points = user_growth.get("currentPoints", 0) + task_config.pointsReward
        await growth_collection.update_one(
            {"userId": userId},
            {
                "$set": {
                    "currentPoints": new_current_points,
                    "lastUpdateTime": current_time
                }
            }
        )
        
        # 标记任务积分已领取
        await task_collection.update_one(
            {
                "userId": userId,
                "taskType": taskType
            },
            {
                "$set": {
                    "pointsClaimed": True,
                    "lastUpdateTime": current_time
                }
            }
        )
        
        return {
            "pointsClaimed": task_config.pointsReward,
            "currentPoints": new_current_points
        }
