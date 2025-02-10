import os

def create_directory_structure():
    # 创建目录结构
    directories = [
        "app",
        "app/api",
        "app/models",
        "app/services",
        "app/database",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    # 创建 __init__.py 文件
    for directory in directories:
        with open(os.path.join(directory, "__init__.py"), "w") as f:
            pass

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_app():
    # 创建目录结构
    create_directory_structure()
    
    # 写入 requirements.txt
    requirements = """fastapi==0.68.0
uvicorn==0.15.0
motor==2.5.1
pydantic==1.8.2
"""
    write_file("requirements.txt", requirements)
    
    # 写入 models/user.py
    user_model = """from pydantic import BaseModel
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
"""
    write_file("app/models/user.py", user_model)
    
    # 写入 database/mongodb.py
    mongodb = """from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        
    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            
    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.client.talk_to_myself[collection_name]
"""
    write_file("app/database/mongodb.py", mongodb)
    
    # 写入 services/user_service.py
    user_service = """from datetime import datetime
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
"""
    write_file("app/services/user_service.py", user_service)
    
    # 写入 api/user.py
    user_api = """from fastapi import APIRouter, HTTPException
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
"""
    write_file("app/api/user.py", user_api)
    
    # 写入 main.py
    main = """from fastapi import FastAPI
from app.api.user import router as user_router
from app.database.mongodb import MongoDB

app = FastAPI(title="Talk to Myself API")

@app.on_event("startup")
async def startup():
    await MongoDB.connect_db()

@app.on_event("shutdown")
async def shutdown():
    await MongoDB.close_db()

app.include_router(user_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    write_file("app/main.py", main)
    
    # 写入启动脚本
    start_script = """#!/bin/bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
    write_file("start.sh", start_script)
    
    # 在 Windows 下也创建一个启动脚本
    start_script_win = """@echo off
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
    write_file("start.bat", start_script_win)

if __name__ == "__main__":
    create_app()
    print("应用创建完成！")
    print("\n使用说明：")
    print("1. 确保已安装 Python 3.7+ 和 MongoDB")
    print("2. 在 Linux/Mac 上运行：")
    print("   chmod +x start.sh")
    print("   ./start.sh")
    print("3. 在 Windows 上运行：")
    print("   start.bat")
    print("\n访问 http://localhost:8000/docs 查看 API 文档")