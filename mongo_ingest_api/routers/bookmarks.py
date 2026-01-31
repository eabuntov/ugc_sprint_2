from fastapi import APIRouter, HTTPException
from datetime import datetime
from db import db
from models import BookmarkCreate

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("/")
async def create_bookmark(data: BookmarkCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()

    await db.bookmarks.insert_one(doc)
    return {"status": "created"}


@router.get("/{user_id}")
async def get_user_bookmarks(user_id: str):
    cursor = db.bookmarks.find({"user_id": user_id})
    return [{**doc, "id": str(doc["_id"])} async for doc in cursor]


@router.delete("/")
async def delete_bookmark(user_id: str, entity_id: str):
    result = await db.bookmarks.delete_one({"user_id": user_id, "entity_id": entity_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Bookmark not found")
    return {"status": "deleted"}
