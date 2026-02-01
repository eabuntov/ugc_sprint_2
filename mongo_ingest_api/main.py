from fastapi import FastAPI
from routers import bookmarks, likes, reviews

from db import db

app = FastAPI(title="User Interactions API")

app.include_router(bookmarks.router)
app.include_router(likes.router)
app.include_router(reviews.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_indexes():
    """
    Initialize the indexes on the Mongo
    Indexes are being created by mongo if not already existing
    """
    await db.bookmarks.create_index(
        [("user_id", 1), ("entity_id", 1)],
        unique=True,
        name="bookmarks_user_entity_uq",
    )

    await db.likes.create_index(
        [("user_id", 1), ("entity_id", 1)],
        unique=True,
        name="likes_user_entity_uq",
    )

    await db.reviews.create_index(
        [("entity_id", 1)],
        name="reviews_entity_idx",
    )
