from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Diary(BaseModel):
    user_id: str
    diary: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    # used for index
    date_int: int
    date: str