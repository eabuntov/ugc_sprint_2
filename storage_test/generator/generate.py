import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from collections import defaultdict

# =========================
# CONFIG (from env)
# =========================
USERS = int(os.getenv("USERS", 1_000_000))
MOVIES = int(os.getenv("MOVIES", 100_000))
LIKES = int(os.getenv("LIKES", 200_000_000))
REVIEWS = int(os.getenv("REVIEWS", 10_000_000))
BOOKMARKS = int(os.getenv("BOOKMARKS", 50_000_000))
SEED = int(os.getenv("SEED", 42))

OUT_DIR = "/data"

random.seed(SEED)
fake = Faker()
fake.seed_instance(SEED)

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 1, 1)

# =========================
# HELPERS
# =========================
def rand_date():
    delta = END_DATE - START_DATE
    return START_DATE + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def zipf_movie():
    # Zipf-like popularity (bounded)
    return min(MOVIES, int(random.paretovariate(1.3)))

def weighted_rating():
    # Bias towards positive ratings
    return random.choices(
        population=list(range(11)),
        weights=[1, 1, 2, 3, 6, 10, 15, 20, 25, 20, 10],
        k=1
    )[0]

# =========================
# LIKES
# =========================
def generate_likes():
    path = f"{OUT_DIR}/likes.jsonl"
    with open(path, "w") as f:
        for _ in range(LIKES):
            record = {
                "user_id": random.randint(1, USERS),
                "movie_id": zipf_movie(),
                "rating": weighted_rating(),
                "created_at": rand_date().isoformat()
            }
            f.write(json.dumps(record) + "\n")

# =========================
# REVIEWS
# =========================
def generate_reviews():
    path = f"{OUT_DIR}/reviews.jsonl"
    review_ids = []

    with open(path, "w") as f:
        for review_id in range(1, REVIEWS + 1):
            movie_id = zipf_movie()
            record = {
                "review_id": review_id,
                "movie_id": movie_id,
                "author_id": random.randint(1, USERS),
                "review_text": fake.text(max_nb_chars=400),
                "user_movie_rating": weighted_rating(),
                "published_at": rand_date().isoformat()
            }
            review_ids.append(review_id)
            f.write(json.dumps(record) + "\n")

    return review_ids

# =========================
# REVIEW REACTIONS
# =========================
def generate_review_reactions(review_ids):
    path = f"{OUT_DIR}/review_reactions.jsonl"

    with open(path, "w") as f:
        for review_id in review_ids:
            reactions = random.randint(0, 50)
            for _ in range(reactions):
                record = {
                    "review_id": review_id,
                    "user_id": random.randint(1, USERS),
                    "is_like": random.choice([0, 1]),
                    "created_at": rand_date().isoformat()
                }
                f.write(json.dumps(record) + "\n")

# =========================
# BOOKMARKS
# =========================
def generate_bookmarks():
    path = f"{OUT_DIR}/bookmarks.jsonl"
    user_bookmarks = defaultdict(set)

    with open(path, "w") as f:
        for _ in range(BOOKMARKS):
            user_id = random.randint(1, USERS)
            movie_id = zipf_movie()

            if movie_id in user_bookmarks[user_id]:
                continue

            user_bookmarks[user_id].add(movie_id)

            record = {
                "user_id": user_id,
                "movie_id": movie_id,
                "created_at": rand_date().isoformat()
            }
            f.write(json.dumps(record) + "\n")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Generating likes...")
    generate_likes()

    print("Generating reviews...")
    review_ids = generate_reviews()

    print("Generating review reactions...")
    generate_review_reactions(review_ids)

    print("Generating bookmarks...")
    generate_bookmarks()

    print("Data generation completed.")
