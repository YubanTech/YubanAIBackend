from fastapi import APIRouter, HTTPException
from app.models.user import CreateUserRequest
from app.services.user_service import UserService

router = APIRouter()

@router.post("/users")
async def create_user(user_request: CreateUserRequest):
    try:
        await UserService.create_user(user_request)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
