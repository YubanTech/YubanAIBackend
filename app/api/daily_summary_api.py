from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime
from app.services.daily_summary_service import DailySummaryService
from app.database.mongodb import MongoDB

router = APIRouter()
daily_summary_service = DailySummaryService()
logger = logging.getLogger(__name__)

@router.post("/daily-summary")
async def generate_daily_summary(user_id: str):
    if not user_id or user_id.strip() == "":
        raise HTTPException(status_code=400, detail="用户ID不能为空")
    try:
        messages = await MongoDB.get_chat_messages(user_id, datetime.now(), datetime.now(), 0, 100)
        
        summary = await daily_summary_service.generate_summary(user_id)
        
        await MongoDB.store_daily_summary(user_id, datetime.now(), summary)
        
        return {"summary": summary}
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}", exc_info=True, extra={"user_id": user_id})
        raise HTTPException(status_code=400, detail="请求参数无效")
    except ConnectionError as ce:
        logger.error(f"数据库连接失败: {str(ce)}", exc_info=True, extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    except Exception as e:
        logger.error(f"生成日报时发生意外错误: {str(e)}", exc_info=True, extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="服务器内部错误")
