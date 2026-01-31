from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BookmarkCreate(BaseModel):
    user_id: str
    entity_type: str
    entity_id: str


class BookmarkOut(BookmarkCreate):
    id: str
    created_at: datetime


class LikeCreate(BookmarkCreate):
    pass


class LikeOut(LikeCreate):
    id: str
    created_at: datetime


class ReviewCreate(BaseModel):
    user_id: str
    entity_type: str
    entity_id: str
    rating: int = Field(ge=1, le=10)
    text: Optional[str]


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(ge=1, le=10)
    text: Optional[str]


class ReviewOut(ReviewCreate):
    id: str
    created_at: datetime
    updated_at: datetime
