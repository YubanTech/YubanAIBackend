from datetime import datetime
from typing import Dict, Any

def user_info_to_dict(user_info) -> Dict[str, Any]:
    return {
        "userId": user_info.userId,
        "userNickName": user_info.userNickName,
        "aiAgentName": user_info.aiAgentName,
        "agentId": user_info.agentId,
        "status": user_info.status,
        "lastUpdateTime": datetime.now().isoformat()
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
        "taskName": user_task.taskName,
        "progress": user_task.progress,
        "isCompleted": user_task.isCompleted,
        "isRewarded": user_task.isRewarded,  # 添加奖励领取状态
        "lastUpdateTime": datetime.now().isoformat()
    }