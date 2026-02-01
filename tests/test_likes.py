import pytest


@pytest.mark.asyncio
async def test_like_success(client, mock_likes_collection):
    payload = {
        "user_id": "user-1",
        "entity_id": "movie-42",
    }

    response = await client.post("/likes/", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "liked"}

    mock_likes_collection.insert_one.assert_awaited_once()
    inserted_doc = mock_likes_collection.insert_one.call_args.args[0]

    assert inserted_doc["user_id"] == "user-1"
    assert inserted_doc["entity_id"] == "movie-42"
    assert "created_at" in inserted_doc


@pytest.mark.asyncio
async def test_count_likes(client, mock_likes_collection):
    response = await client.get("/likes/count", params={"entity_id": "movie-42"})

    assert response.status_code == 200
    assert response.json() == {
        "entity_id": "movie-42",
        "likes": 3,
    }

    mock_likes_collection.count_documents.assert_awaited_once_with(
        {"entity_id": "movie-42"}
    )


@pytest.mark.asyncio
async def test_unlike_success(client, mock_likes_collection):
    response = await client.delete(
        "/likes/",
        params={"user_id": "user-1", "entity_id": "movie-42"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "unliked"}

    mock_likes_collection.delete_one.assert_awaited_once_with(
        {"user_id": "user-1", "entity_id": "movie-42"}
    )

