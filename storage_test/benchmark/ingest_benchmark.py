import time
import json
import os
from pathlib import Path

from clickhouse_driver import Client as CHClient
from pymongo import MongoClient, UpdateOne

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/data/results")
RESULTS_DIR.mkdir(exist_ok=True)

# =========================
# CONFIG
# =========================
CH_CONFIG = {
    "host": os.getenv("CLICKHOUSE_HOST", "clickhouse"),
    "database": os.getenv("CLICKHOUSE_DB", "analytics"),
    "user": os.getenv("CLICKHOUSE_USER", "benchmark"),
    "password": os.getenv("CLICKHOUSE_PASSWORD", "benchmark"),
}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
BATCH_SIZE_CH = int(os.getenv("CH_BATCH_SIZE", 10_000))
BATCH_SIZE_MONGO = int(os.getenv("MONGO_BATCH_SIZE", 1_000))

# =========================
# CLIENTS
# =========================
ch = CHClient(**CH_CONFIG)
mongo = MongoClient(MONGO_URI)["analytics"]

# =========================
# UTIL
# =========================
def timed(label, fn):
    start = time.perf_counter()
    count = fn()
    elapsed = time.perf_counter() - start
    return {
        "label": label,
        "rows": count,
        "seconds": elapsed,
        "rows_per_sec": count / elapsed if elapsed > 0 else None,
    }

# =========================
# CLICKHOUSE INGEST
# =========================
def ch_ingest(file, table, columns):
    rows = []
    total = 0

    with open(file) as f:
        for line in f:
            record = json.loads(line)
            rows.append(tuple(record[c] for c in columns))

            if len(rows) >= BATCH_SIZE_CH:
                ch.execute(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES",
                    rows,
                )
                total += len(rows)
                rows.clear()

        if rows:
            ch.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES",
                rows,
            )
            total += len(rows)

    return total

# =========================
# MONGODB INGEST
# =========================
def mongo_likes(file):
    ops = []
    total = 0

    for line in open(file):
        r = json.loads(line)
        ops.append(
            UpdateOne(
                {"movie_id": r["movie_id"]},
                {
                    "$push": {"likes": r},
                    "$inc": {
                        "likes_count": 1 if r["rating"] >= 7 else 0,
                        "dislikes_count": 1 if r["rating"] <= 4 else 0,
                    },
                },
                upsert=True,
            )
        )

        if len(ops) >= BATCH_SIZE_MONGO:
            mongo.movies.bulk_write(ops)
            total += len(ops)
            ops.clear()

    if ops:
        mongo.movies.bulk_write(ops)
        total += len(ops)

    return total

def mongo_simple(file, collection, key):
    ops = []
    total = 0

    for line in open(file):
        r = json.loads(line)
        ops.append(
            UpdateOne(
                {key: r[key]},
                {"$push": r},
                upsert=True,
            )
        )

        if len(ops) >= BATCH_SIZE_MONGO:
            mongo[collection].bulk_write(ops)
            total += len(ops)
            ops.clear()

    if ops:
        mongo[collection].bulk_write(ops)
        total += len(ops)

    return total

# =========================
# ORCHESTRATION
# =========================
def run():
    results = {
        "clickhouse": {},
        "mongodb": {},
        "meta": {
            "batch_size_ch": BATCH_SIZE_CH,
            "batch_size_mongo": BATCH_SIZE_MONGO,
        },
    }

    # -------- ClickHouse --------
    results["clickhouse"]["movie_likes"] = timed(
        "ch_movie_likes",
        lambda: ch_ingest(
            DATA_DIR / "likes.jsonl",
            "movie_likes",
            ["user_id", "movie_id", "rating", "created_at"],
        ),
    )

    results["clickhouse"]["reviews"] = timed(
        "ch_reviews",
        lambda: ch_ingest(
            DATA_DIR / "reviews.jsonl",
            "reviews",
            [
                "review_id",
                "movie_id",
                "author_id",
                "review_text",
                "user_movie_rating",
                "published_at",
            ],
        ),
    )

    results["clickhouse"]["review_reactions"] = timed(
        "ch_review_reactions",
        lambda: ch_ingest(
            DATA_DIR / "review_reactions.jsonl",
            "review_reactions",
            ["review_id", "user_id", "is_like", "created_at"],
        ),
    )

    results["clickhouse"]["bookmarks"] = timed(
        "ch_bookmarks",
        lambda: ch_ingest(
            DATA_DIR / "bookmarks.jsonl",
            "bookmarks",
            ["user_id", "movie_id", "created_at"],
        ),
    )

    # -------- MongoDB --------
    results["mongodb"]["movie_likes"] = timed(
        "mongo_movie_likes",
        lambda: mongo_likes(DATA_DIR / "likes.jsonl"),
    )

    results["mongodb"]["reviews"] = timed(
        "mongo_reviews",
        lambda: mongo_simple(
            DATA_DIR / "reviews.jsonl",
            "reviews",
            "review_id",
        ),
    )

    results["mongodb"]["bookmarks"] = timed(
        "mongo_bookmarks",
        lambda: mongo_simple(
            DATA_DIR / "bookmarks.jsonl",
            "user_bookmarks",
            "user_id",
        ),
    )

    # =========================
    # WRITE RESULTS
    # =========================
    out = RESULTS_DIR / "ingest_benchmark.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Benchmark results written to {out}")

# =========================
# ENTRYPOINT
# =========================
if __name__ == "__main__":
    run()
