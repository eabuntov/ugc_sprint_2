import time
from pymongo import MongoClient, WriteConcern

client = MongoClient("mongodb://mongo:27017")
db = client.analytics

likes = db.likes.with_options(write_concern=WriteConcern(w="majority"))


def insert_like(user_id, movie_id, rating):
    ts = time.time()
    likes.insert_one(
        {"user_id": user_id, "movie_id": movie_id, "rating": rating, "ts": ts}
    )
    return ts


def is_like_visible(user_id, movie_id):
    return likes.count_documents({"user_id": user_id, "movie_id": movie_id}) > 0


def measure_visibility(user_id, movie_id, rating):
    write_ts = insert_like(user_id, movie_id, rating)

    start = time.time()
    while time.time() - start < 1.0:
        if is_like_visible(user_id, movie_id):
            return (time.time() - write_ts) * 1000
        time.sleep(0.005)

    return None


def run_test(n=1000):
    latencies = []

    for i in range(n):
        latency = measure_visibility(user_id=1000 + i, movie_id=42, rating=8)
        if latency is not None:
            latencies.append(latency)

    return latencies
