import itertools
import random
import time

from clickhouse_driver import Client

client = Client(
    host="clickhouse", database="analytics", user="benchmark", password="benchmark"
)


def insert_like(event):
    client.execute(
        "INSERT INTO movie_likes VALUES",
        [(event["user_id"], event["movie_id"], event["rating"], event["created_at"])],
    )

# ---- configuration ----

MOVIE_ID_RANGE = (1, 50_000)
USER_ID_RANGE = (1, 100_000)
REVIEW_ID_RANGE = (1, 5_000_000)

EVENT_WEIGHTS = {
    "movie_like": 0.45,
    "movie_dislike": 0.15,
    "bookmark": 0.25,
    "review_reaction": 0.15,
}

# deterministic randomness
_rng = random.Random(42)

_event_counter = itertools.count(1)

def get_next_event() -> dict:
    event_id = next(_event_counter)
    now = time.time()

    event_type = _rng.choices(
        population=list(EVENT_WEIGHTS.keys()),
        weights=list(EVENT_WEIGHTS.values()),
        k=1
    )[0]

    if event_type == "movie_like":
        payload = {
            "user_id": _rng.randint(*USER_ID_RANGE),
            "movie_id": _rng.randint(*MOVIE_ID_RANGE),
            "rating": _rng.randint(6, 10),
        }

    elif event_type == "movie_dislike":
        payload = {
            "user_id": _rng.randint(*USER_ID_RANGE),
            "movie_id": _rng.randint(*MOVIE_ID_RANGE),
            "rating": _rng.randint(0, 4),
        }

    elif event_type == "bookmark":
        payload = {
            "user_id": _rng.randint(*USER_ID_RANGE),
            "movie_id": _rng.randint(*MOVIE_ID_RANGE),
        }

    elif event_type == "review_reaction":
        payload = {
            "review_id": _rng.randint(*REVIEW_ID_RANGE),
            "user_id": _rng.randint(*USER_ID_RANGE),
            "reaction": _rng.choice(["like", "dislike"]),
        }

    else:
        raise ValueError(f"Unknown event type: {event_type}")

    return {
        "event_id": event_id,
        "type": event_type,
        "payload": payload,
        "ts": now,
    }


while True:
    event = get_next_event()  # generator / kafka / socket
    insert_like(event)
