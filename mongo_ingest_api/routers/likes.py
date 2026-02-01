from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from db import db
from models import LikeCreate

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post("/")
async def like(data: LikeCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()

    await db.likes.insert_one(doc)
    return {"status": "liked"}


@router.get("/count")
async def count_likes(entity_id: str):
    return {
        "entity_id": entity_id,
        "likes": await db.likes.count_documents({"entity_id": entity_id}),
    }


@router.delete("/")
async def unlike(user_id: str, entity_id: str):
    result = await db.likes.delete_one({"user_id": user_id, "entity_id": entity_id})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Like not found")
    return {"status": "unliked"}
