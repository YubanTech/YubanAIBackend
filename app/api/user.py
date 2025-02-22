from fastapi import APIRouter, HTTPException
from app.models.user import (
    CreateUserRequest, UpdateUserRequest, GetUserStatusRequest,
    GetUserGrowthRequest, GetUserStatusResponse, GetUserGrowthResponse,
    TaskType  # 添加 TaskType 导入
)
from app.services.user_service import UserService

router = APIRouter()

@router.post("/users")
async def create_user(user_request: CreateUserRequest):
    try:
        await UserService.create_user(user_request)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{userId}")
async def update_user(userId: str, update_request: UpdateUserRequest):
    try:
        await UserService.update_user(userId, update_request)
        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{userId}/status", response_model=GetUserStatusResponse)
async def get_user_status(userId: str):
    try:
        result = await UserService.get_user_status(userId)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        result = await UserService.update_user_growth(userId, taskType)
        if not result:
            raise HTTPException(status_code=400, detail="Invalid task or task already completed")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{userId}/tasks/{taskType}/claim")
async def claim_task_reward(userId: str, taskType: TaskType):
    try:
        result = await UserService.claim_task_reward(userId, taskType)
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Invalid task or task not completed or reward already claimed"
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
