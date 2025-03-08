from datetime import datetime
from typing import Dict, Any
import time

def user_info_to_dict(user_info) -> Dict[str, Any]:
    current_time = datetime.now().isoformat()
    # 获取当前毫秒时间戳
    current_ms_timestamp = int(time.time() * 1000)
    
    return {
        "userId": user_info.userId,
        "userNickName": user_info.userNickName,
        "aiAgentName": user_info.aiAgentName,
        "agentId": user_info.agentId,
        "status": user_info.status,
        "lastUpdateTime": current_time,
        "createdTime": getattr(user_info, 'createdTime', current_ms_timestamp)  # 使用毫秒时间戳
    }

def user_growth_to_dict(user_growth) -> Dict[str, Any]:
    return {
        "userId": user_growth.userId,
        "currentPoints": user_growth.currentPoints,
        "totalPoints": user_growth.totalPoints,
        "lastUpdateTime": datetime.now().isoformat()
    }

def user_task_to_dict(user_task) -> Dict[str, Any]:
    return {
        "userId": user_task.userId,
        "taskType": user_task.taskType,
        "progress": user_task.progress,
        "isCompleted": user_task.isCompleted,
        "lastUpdateTime": datetime.now().isoformat()
    }