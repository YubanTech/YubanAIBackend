from fastapi import APIRouter, HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from app.models.tarot import TarotResponse, TarotCard
from app.services.tarot_service import TarotService

router = APIRouter()

@router.get("/random", response_model=TarotResponse)
async def get_random_tarot_cards():
    """获取4张随机塔罗牌"""
    try:
        logger.debug("Getting random tarot cards")
        cards = await TarotService.get_random_cards(4)
        return TarotResponse(cards=cards)
    except Exception as e:
        logger.error(f"Error getting random tarot cards: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))