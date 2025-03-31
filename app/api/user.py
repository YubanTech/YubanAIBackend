from fastapi import APIRouter, HTTPException
import logging
import traceback  # 添加traceback模块

# 设置更详细的日志级别
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from app.models.user import (
    CreateUserRequest, UpdateUserRequest, GetUserStatusRequest,
    GetUserGrowthRequest, GetUserStatusResponse, GetUserGrowthResponse,
    TaskType, WxLoginRequest, LoginResponse  # 添加 TaskType 和 WxLoginRequest 导入
)
from app.services.user_service import UserService

router = APIRouter()

@router.post("/users")
async def create_user(user_request: CreateUserRequest):
    try:
        logger.debug(f"Creating user with request: {user_request}")
        await UserService.create_user(user_request)
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        logger.error(traceback.format_exc())  # 打印完整的异常堆栈
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{userId}")
async def update_user(userId: str, update_request: UpdateUserRequest):
    try:
        logger.debug(f"Updating user {userId} with request: {update_request}")
        await UserService.update_user(userId, update_request)
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{userId}/status", response_model=GetUserStatusResponse)
async def get_user_status(userId: str):
    try:
        logger.debug(f"Getting status for user: {userId}")
        result = await UserService.get_user_status(userId)
        logger.debug(f"User status result: {result}")
        if not result:
            logger.warning(f"User not found: {userId}")
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except Exception as e:
        logger.error(f"Error getting user status: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/users/{userId}/growth", response_model=GetUserGrowthResponse)
async def get_user_growth(userId: str):
    try:
        result = await UserService.get_user_growth(userId)
        if not result:
            raise HTTPException(status_code=404, detail="User growth not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{userId}/growth/{taskType}")
async def update_user_growth(userId: str, taskType: TaskType):
    try:
        result = await UserService.mark_task_completed(userId, taskType)
        if not result:
            raise HTTPException(status_code=400, detail="Invalid task or task already completed")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login/wechat", response_model=LoginResponse)
async def login_with_wechat(login_request: WxLoginRequest):
    try:
        logger.debug(f"处理微信登录请求: {login_request.nickName}")
        result = await UserService.login_with_wechat(login_request)
        if not result:
            logger.warning("登录失败")
            raise HTTPException(status_code=400, detail="登录失败，请重试")
        return result
    except Exception as e:
        logger.error(f"登录处理错误: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.post("/users/{userId}/growth/{taskType}/claim")
async def claim_task_points(userId: str, taskType: TaskType):
    """领取指定任务的积分"""
    try:
        result = await UserService.claim_task_points(userId, taskType)
        if not result:
            raise HTTPException(status_code=400, detail="Task not completed or points already claimed")
        return {
            "message": "Points claimed successfully",
            "taskType": taskType,
            "pointsClaimed": result.get("pointsClaimed", 0),
            "currentPoints": result.get("currentPoints", 0)
        }
    except Exception as e:
        logger.error(f"Error claiming points: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
