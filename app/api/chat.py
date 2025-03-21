from fastapi import APIRouter, HTTPException
from pydantic import BaseModel  # Add this import
from datetime import datetime
from typing import List, Optional
from app.models.chat import ChatHistoryItem, ChatHistoryResponse
from app.services.chat_service import ChatService

router = APIRouter()

class ChatRequest(BaseModel):
    userId: str
    message: str

class ChatResponse(BaseModel):
    message: str
    timestamp: str

class ChatHistoryRequest(BaseModel):
    userId: str
    start_time: datetime
    end_time: datetime

class ChatHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryItem]
    total: int  # 添加总记录数
    current_page: int  # 添加当前页码

@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    userId: str, 
    page: int = 1,  # 当前页码，默认第1页
    start_time: Optional[datetime] = None,  # 可选的开始时间
    end_time: Optional[datetime] = None,  # 可选的结束时间
    page_size: int = 20  # 每页记录数，默认20条
):
    try:
        history, total = await ChatService.get_chat_history(
            user_id=userId,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size
        )
        return ChatHistoryResponse(
            history=history,
            total=total,
            current_page=page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SetAgentNameRequest(BaseModel):
    userId: str
    agent_name: str

@router.post("/chat/set_agent_name")
async def set_agent_name(request: SetAgentNameRequest):
    try:
        chat_service = ChatService()
        await chat_service.update_agent_name(request.userId, request.agent_name)
        return {"message": f"Agent name set to {request.agent_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        chat_service = ChatService()
        
        # 获取 agent 昵称
        agent_name = await chat_service.get_agent_name(request.userId)
        
        response = await chat_service.generate_response(
            user_id=request.userId,
            message=request.message,
        )
        
        return ChatResponse(
            message=response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))