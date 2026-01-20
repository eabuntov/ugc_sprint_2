from pymongo import MongoClient, UpdateOne
import json

db = MongoClient("mongodb://mongodb:27017")["analytics"]

def bulk_likes(path):
    ops = []
    for line in open(path):
        r = json.loads(line)
        ops.append(
            UpdateOne(
                {"movie_id": r["movie_id"]},
                {
                    "$push": {"likes": r},
                    "$inc": {
                        "likes_count": 1 if r["rating"] >= 7 else 0,
                        "dislikes_count": 1 if r["rating"] <= 4 else 0
                    }
                },
                upsert=True
            )
        )
        if len(ops) == 1000:
            db.movies.bulk_write(ops)
            ops.clear()
    if ops:
        db.movies.bulk_write(ops)

def bulk_bookmarks(path):
    ops = []
    for line in open(path):
        r = json.loads(line)
        ops.append(
            UpdateOne(
                {"user_id": r["user_id"]},
                {"$push": {"movies": r}},
                upsert=True
            )
        )
        if len(ops) == 1000:
            db.user_bookmarks.bulk_write(ops)
            ops.clear()
    if ops:
        db.user_bookmarks.bulk_write(ops)

bulk_likes("/data/likes.jsonl")
bulk_bookmarks("/data/bookmarks.jsonl")
