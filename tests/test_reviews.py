from datetime import datetime

import pytest
from bson import ObjectId

from tests.conftest import AsyncCursor


@pytest.mark.asyncio
async def test_create_review(client, mock_reviews_collection):
    payload = {
        "user_id": "user-1",
        "entity_id": "movie-42",
        "rating": 5,
        "text": "Great movie",
    }

    response = await client.post("/reviews/", json=payload)

    assert response.status_code == 200
    assert "id" in response.json()

    mock_reviews_collection.insert_one.assert_awaited_once()

    inserted_doc = mock_reviews_collection.insert_one.call_args.args[0]
    assert inserted_doc["user_id"] == "user-1"
    assert inserted_doc["entity_id"] == "movie-42"
    assert "created_at" in inserted_doc
    assert "updated_at" in inserted_doc

@pytest.mark.asyncio
async def test_get_reviews(client, mock_reviews_collection):
    review_id = ObjectId()
    docs = [
        {
            "_id": review_id,
            "user_id": "user-1",
            "entity_id": "movie-42",
            "rating": 4,
            "text": "Nice",
            "created_at": datetime.utcnow(),
        }
    ]

    mock_reviews_collection.find.return_value = AsyncCursor(docs)

    response = await client.get("/reviews/entity/movie-42")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(review_id)
    assert data[0]["entity_id"] == "movie-42"

    mock_reviews_collection.find.assert_called_once_with(
        {"entity_id": "movie-42"}
    )

@pytest.mark.asyncio
async def test_update_review_success(client, mock_reviews_collection):
    review_id = str(ObjectId())
    payload = {
        "rating": 3,
        "text": "Updated review",
    }

    response = await client.put(f"/reviews/{review_id}", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "updated"}

    mock_reviews_collection.update_one.assert_awaited_once()

    query, update = mock_reviews_collection.update_one.call_args.args
    assert query["_id"] == ObjectId(review_id)
    assert "$set" in update
    assert update["$set"]["rating"] == 3
    assert update["$set"]["text"] == "Updated review"
    assert "updated_at" in update["$set"]

@pytest.mark.asyncio
async def test_update_review_not_found(client, mock_reviews_collection):
    mock_reviews_collection.update_one.return_value.matched_count = 0

    response = await client.put(
        f"/reviews/{ObjectId()}",
        json={"rating": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"

@pytest.mark.asyncio
async def test_delete_review_success(client, mock_reviews_collection):
    review_id = str(ObjectId())

    response = await client.delete(f"/reviews/{review_id}")

    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    mock_reviews_collection.delete_one.assert_awaited_once_with(
        {"_id": ObjectId(review_id)}
    )

@pytest.mark.asyncio
async def test_delete_review_not_found(client, mock_reviews_collection):
    mock_reviews_collection.delete_one.return_value.deleted_count = 0

    response = await client.delete(f"/reviews/{ObjectId()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"

