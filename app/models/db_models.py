from datetime import datetime
from typing import Dict, Any
import time
from app.models.user import UserInfo, UserGrowth, UserTask, GrowthTasks

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

def user_task_to_dict(task: UserTask) -> dict:
    # 获取任务配置信息
    task_config = GrowthTasks.get_all_tasks().get(task.taskType.value)  # 使用 .value 获取枚举值
    if not task_config:
        print(f"Warning: 未找到任务配置 {task.taskType}")
        return {
            "userId": task.userId,
            "taskType": task.taskType,
            "progress": task.progress,
            "isCompleted": task.isCompleted,
            "lastUpdateTime": task.lastUpdateTime,
            "taskName": "未知任务",
            "requiredProgress": 0,
            "pointsReward": 0
        }
    
    return {
        "userId": task.userId,
        "taskType": task.taskType,
        "progress": task.progress,
        "isCompleted": task.isCompleted,
        "lastUpdateTime": task.lastUpdateTime,
        "taskName": task_config.name,
        "requiredProgress": task_config.requiredProgress,
        "pointsReward": task_config.pointsReward
    }