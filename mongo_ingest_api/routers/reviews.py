from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from bson import ObjectId
from db import db
from models import ReviewCreate, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/")
async def create_review(data: ReviewCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.now()
    doc["updated_at"] = datetime.now()

    res = await db.reviews.insert_one(doc)
    return {"id": str(res.inserted_id)}


@router.get("/entity/{entity_id}")
async def get_reviews(entity_id: str):
    cursor = db.reviews.find({"entity_id": entity_id})
    return [{**doc, "id": str(doc["_id"])} async for doc in cursor]


@router.put("/{review_id}")
async def update_review(review_id: str, data: ReviewUpdate):
    result = await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {
            "$set": {
                **data.model_dump(exclude_none=True),
                "updated_at": datetime.utcnow(),
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    return {"status": "updated"}


@router.delete("/{review_id}")
async def delete_review(review_id: str):
    result = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    return {"status": "deleted"}
