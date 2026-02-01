import pytest


@pytest.mark.asyncio
async def test_create_bookmark(client, mock_bookmarks_collection):
    payload = {
        "user_id": "user-1",
        "entity_id": "movie-42",
    }

    response = await client.post("/bookmarks/", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "created"}

    mock_bookmarks_collection.insert_one.assert_awaited_once()

    inserted_doc = mock_bookmarks_collection.insert_one.call_args.args[0]
    assert inserted_doc["user_id"] == "user-1"
    assert inserted_doc["entity_id"] == "movie-42"
    assert "created_at" in inserted_doc

@pytest.mark.asyncio
async def test_get_user_bookmarks(client, mock_bookmarks_collection):
    docs = [
        {
            "_id": "fake-id-1",
            "user_id": "user-1",
            "entity_id": "movie-42",
            "created_at": datetime.utcnow(),
        },
        {
            "_id": "fake-id-2",
            "user_id": "user-1",
            "entity_id": "movie-43",
            "created_at": datetime.utcnow(),
        },
    ]

    mock_bookmarks_collection.find.return_value = AsyncCursor(docs)

    response = await client.get("/bookmarks/user-1")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] == "fake-id-1"
    assert data[1]["entity_id"] == "movie-43"

    mock_bookmarks_collection.find.assert_called_once_with(
        {"user_id": "user-1"}
    )

@pytest.mark.asyncio
async def test_delete_bookmark_success(client, mock_bookmarks_collection):
    response = await client.delete(
        "/bookmarks/",
        params={"user_id": "user-1", "entity_id": "movie-42"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    mock_bookmarks_collection.delete_one.assert_awaited_once_with(
        {"user_id": "user-1", "entity_id": "movie-42"}
    )

@pytest.mark.asyncio
async def test_delete_bookmark_not_found(client, mock_bookmarks_collection):
    mock_bookmarks_collection.delete_one.return_value.deleted_count = 0

    response = await client.delete(
        "/bookmarks/",
        params={"user_id": "user-x", "entity_id": "movie-x"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Bookmark not found"
