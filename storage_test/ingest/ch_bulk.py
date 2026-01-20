from clickhouse_driver import Client
import json

client = Client(
    host="clickhouse",
    database="analytics",
    user="benchmark",
    password="benchmark"
)

def bulk_insert(file_path, table, columns):
    batch = []
    with open(file_path) as f:
        for line in f:
            row = json.loads(line)
            batch.append(tuple(row[c] for c in columns))
            if len(batch) == 10_000:
                client.execute(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES",
                    batch
                )
                batch.clear()
        if batch:
            client.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES",
                batch
            )

bulk_insert(
    "/data/likes.jsonl",
    "movie_likes",
    ["user_id", "movie_id", "rating", "created_at"]
)

bulk_insert(
    "/data/reviews.jsonl",
    "reviews",
    ["review_id", "movie_id", "author_id",
     "review_text", "user_movie_rating", "published_at"]
)

bulk_insert(
    "/data/review_reactions.jsonl",
    "review_reactions",
    ["review_id", "user_id", "is_like", "created_at"]
)

bulk_insert(
    "/data/bookmarks.jsonl",
    "bookmarks",
    ["user_id", "movie_id", "created_at"]
)
