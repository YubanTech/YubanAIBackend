from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.diary_service import DiaryService
import asyncio

router = APIRouter()

class DiaryItem(BaseModel):
    diary: str
    date: str
    date_int: int

class DiaryResponse(BaseModel):
    diary_list: List[DiaryItem]

@router.get("/diary/get_diarys", response_model=DiaryResponse)
async def get_diarys(userId: str, start_day: int, end_day: int):
    try:


        diary_service = DiaryService()
        diarys = await diary_service.get_diary_summary(userId, start_day, end_day)

        print("diarys:", diarys)
        res = list()
        for diary in diarys:
            item = DiaryItem(
                diary=diary.diary,
                date=diary.date,
                date_int=diary.date_int
            )
            res.append(item)

        return DiaryResponse(
            diary_list=res
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diary/get_diarys_last7day", response_model=DiaryResponse)
async def get_diarys_last7day(userId: str):
    start_day = int(datetime.today().strftime("%Y%m%d")) - 7
    end_day = int(datetime.today().strftime("%Y%m%d")) - 1

    return await get_diarys(userId, start_day, end_day)


def check_date_int(date_int: int) -> bool:
    date_str = str(date_int)

    # 校验是否为 8 位纯数字
    if len(date_str) != 8 or not date_str.isdigit():
        return False

    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
    except ValueError as e:
        return False

    return True