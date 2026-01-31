import os
import time
import random
import asyncio
from collections import defaultdict

from clickhouse_driver import Client as CHClient
from pymongo import MongoClient

# =========================
# CONFIG
# =========================
SEED = int(os.getenv("SEED", 42))
DURATION = int(os.getenv("DURATION", 300))  # seconds
CONCURRENCY = int(os.getenv("CONCURRENCY", 50))
USERS = int(os.getenv("USERS", 1_000_000))
MOVIES = int(os.getenv("MOVIES", 100_000))

random.seed(SEED)

# =========================
# CLIENTS
# =========================
ch = CHClient(
    host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
    database=os.getenv("CLICKHOUSE_DB", "analytics"),
    user=os.getenv("CLICKHOUSE_USER", "benchmark"),
    password=os.getenv("CLICKHOUSE_PASSWORD", "benchmark"),
)

mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017"))["analytics"]

# =========================
# METRICS
# =========================
latencies = {
    "clickhouse": defaultdict(list),
    "mongodb": defaultdict(list),
}


# =========================
# CLICKHOUSE QUERIES
# =========================
def ch_user_likes(user_id):
    return ch.execute(
        "SELECT movie_id, rating FROM movie_likes WHERE user_id = %(u)s",
        {"u": user_id},
    )


def ch_movie_reactions(movie_id):
    return ch.execute(
        """
        SELECT
            countIf(rating >= 7) AS likes,
            countIf(rating <= 4) AS dislikes
        FROM movie_likes
        WHERE movie_id = %(m)s
        """,
        {"m": movie_id},
    )


def ch_user_bookmarks(user_id):
    return ch.execute(
        "SELECT movie_id FROM bookmarks WHERE user_id = %(u)s",
        {"u": user_id},
    )


def ch_movie_avg(movie_id):
    return ch.execute(
        "SELECT avg(rating) FROM movie_likes WHERE movie_id = %(m)s",
        {"m": movie_id},
    )


# =========================
# MONGODB QUERIES
# =========================
def mongo_user_likes(user_id):
    return mongo.movies.find(
        {"likes.user_id": user_id},
        {"movie_id": 1, "likes.$": 1},
    )


def mongo_movie_reactions(movie_id):
    return mongo.movies.find_one(
        {"movie_id": movie_id},
        {"likes_count": 1, "dislikes_count": 1},
    )


def mongo_user_bookmarks(user_id):
    return mongo.user_bookmarks.find_one(
        {"user_id": user_id},
        {"movies": 1},
    )


def mongo_movie_avg(movie_id):
    return mongo.movies.find_one(
        {"movie_id": movie_id},
        {"avg_rating": 1},
    )


# =========================
# WORKER
# =========================
async def worker(db, stop_at):
    while time.time() < stop_at:
        user_id = random.randint(1, USERS)
        movie_id = random.randint(1, MOVIES)

        queries = [
            (
                "user_likes",
                lambda: ch_user_likes(user_id)
                if db == "clickhouse"
                else mongo_user_likes(user_id),
            ),
            (
                "movie_reactions",
                lambda: ch_movie_reactions(movie_id)
                if db == "clickhouse"
                else mongo_movie_reactions(movie_id),
            ),
            (
                "user_bookmarks",
                lambda: ch_user_bookmarks(user_id)
                if db == "clickhouse"
                else mongo_user_bookmarks(user_id),
            ),
            (
                "movie_avg",
                lambda: ch_movie_avg(movie_id)
                if db == "clickhouse"
                else mongo_movie_avg(movie_id),
            ),
        ]

        name, fn = random.choice(queries)
        start = time.perf_counter()
        fn()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        latencies[db][name].append(elapsed)

        await asyncio.sleep(0)


# =========================
# RUNNER
# =========================
async def run_db(db):
    stop_at = time.time() + DURATION
    await asyncio.gather(*[worker(db, stop_at) for _ in range(CONCURRENCY)])


def percentile(values, p):
    values = sorted(values)
    if not values:
        return None
    k = int(len(values) * p / 100)
    return values[min(k, len(values) - 1)]


def report():
    for db in latencies:
        print(f"\n=== {db.upper()} ===")
        for q, values in latencies[db].items():
            print(
                f"{q:20s} "
                f"p50={percentile(values, 50):.2f}ms "
                f"p95={percentile(values, 95):.2f}ms "
                f"p99={percentile(values, 99):.2f}ms "
                f"n={len(values)}"
            )


# =========================
# ENTRYPOINT
# =========================
async def main():
    print("Running ClickHouse read benchmark...")
    await run_db("clickhouse")

    print("Running MongoDB read benchmark...")
    await run_db("mongodb")

    report()


if __name__ == "__main__":
    asyncio.run(main())
