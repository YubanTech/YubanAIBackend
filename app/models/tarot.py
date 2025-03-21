from pydantic import BaseModel
from typing import List
from enum import Enum

class TarotType(str, Enum):
    MAJOR = "major"    # 大阿尔卡纳
    WANDS = "wands"    # 权杖
    CUPS = "cups"      # 圣杯
    SWORDS = "swords"  # 宝剑
    PENTACLES = "pentacles"  # 星币

class TarotCard(BaseModel):
    id: str
    name: str
    name_en: str
    image_url: str
    description: str
    keywords: List[str]
    analysis: str
    affirmation: str
    type: TarotType    # 添加类型字段

class TarotResponse(BaseModel):
    cards: List[TarotCard]