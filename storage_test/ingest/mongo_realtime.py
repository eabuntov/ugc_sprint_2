from pymongo import MongoClient

db = MongoClient("mongodb://mongodb:27017")["analytics"]

def insert_like(event):
    db.movies.update_one(
        {"movie_id": event["movie_id"]},
        {
            "$push": {"likes": event},
            "$inc": {
                "likes_count": 1 if event["rating"] >= 7 else 0,
                "dislikes_count": 1 if event["rating"] <= 4 else 0
            }
        },
        upsert=True
    )
