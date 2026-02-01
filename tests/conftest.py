import pytest
from bson import ObjectId
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock

from mongo_ingest_api.routers import bookmarks, likes, reviews

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(bookmarks.router)
    app.include_router(likes.router)
    app.include_router(reviews.router)
    return app


@pytest.fixture
async def client(app):
    async with AsyncClient(base_url="http://mongo_ingest_api") as client:
        yield client


@pytest.fixture
def mock_likes_collection(monkeypatch):
    """
    Mock db.likes collection with async methods.
    """
    mock_likes = AsyncMock()

    # Default behaviors
    mock_likes.insert_one.return_value = None
    mock_likes.count_documents.return_value = 3
    mock_likes.delete_one.return_value.deleted_count = 1

    # Patch db.likes
    monkeypatch.setattr("mongo_ingest_api.routers.likes.db.likes", mock_likes)

    return mock_likes

class AsyncCursor:
    def __init__(self, docs):
        self.docs = docs

    def __aiter__(self):
        self._iter = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
def mock_reviews_collection(monkeypatch):
    mock_reviews = AsyncMock()

    # insert_one
    mock_reviews.insert_one.return_value.inserted_id = ObjectId()

    # find
    mock_reviews.find.return_value = AsyncCursor([])

    # update_one
    mock_reviews.update_one.return_value.matched_count = 1

    # delete_one
    mock_reviews.delete_one.return_value.deleted_count = 1

    monkeypatch.setattr("mongo_ingest_api.routers.reviews.db.reviews", mock_reviews)

    return mock_reviews


@pytest.fixture
def mock_bookmarks_collection(monkeypatch):
    mock_bookmarks = AsyncMock()

    # insert_one
    mock_bookmarks.insert_one.return_value = None

    # find
    mock_bookmarks.find.return_value = AsyncCursor([])

    # delete_one
    mock_bookmarks.delete_one.return_value.deleted_count = 1

    monkeypatch.setattr("mongo_ingest_api.routers.bookmarks.db.bookmarks", mock_bookmarks)

    return mock_bookmarks
