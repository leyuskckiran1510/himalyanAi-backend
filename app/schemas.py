from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    username: str
    email: EmailStr
    profile_pic: Optional[str] = None
    joined_at: datetime

    class Config:
        from_attributes = True
