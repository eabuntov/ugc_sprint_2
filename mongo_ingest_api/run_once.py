import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING


async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["content"]

    await db.bookmarks.create_index(
        [("user_id", ASCENDING), ("entity_id", ASCENDING)],
        unique=True,
        name="uniq_user_entity_bookmark",
    )

    await db.likes.create_index(
        [("user_id", ASCENDING), ("entity_id", ASCENDING)],
        unique=True,
        name="uniq_user_entity_like",
    )

    await db.reviews.create_index(
        [("entity_id", ASCENDING)],
        name="idx_reviews_entity",
    )

    print("Indexes created successfully")


if __name__ == "__main__":
    asyncio.run(main())
