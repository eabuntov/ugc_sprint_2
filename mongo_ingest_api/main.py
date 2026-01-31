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
    await db.bookmarks.create_index([("user_id", 1), ("entity_id", 1)], unique=True)
    await db.likes.create_index([("user_id", 1), ("entity_id", 1)], unique=True)
    await db.reviews.create_index([("entity_id", 1)])
