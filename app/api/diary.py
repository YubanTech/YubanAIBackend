from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.diary_service import DiaryService

router = APIRouter()

class DiaryRequest(BaseModel):
    userId: str

class DiaryItem(BaseModel):
    diary: str
    date: str
    date_int: int

class DiaryResponse(BaseModel):
    diary_list: List[DiaryItem]

@router.post("/diary/get_diarys")
async def get(request: DiaryRequest):
    try:
        diary_service = DiaryService()
        diarys = await diary_service.get_diary_summary(request.userId)

        res = list()
        for diary in diarys:
            item = DiaryItem(
                diary=diary.diary,
                date=diary.date,
                date_int=diary.date_index
            )
            res.append(item)

        return DiaryResponse(
            diary_list=res
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))