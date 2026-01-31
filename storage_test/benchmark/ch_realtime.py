import time
from clickhouse_driver import Client

client = Client(host="clickhouse", database="analytics")

POLL_INTERVAL = 0.01  # 10 ms
TIMEOUT = 5.0  # seconds


def insert_like(user_id, movie_id, rating):
    ts = time.time()
    client.execute("INSERT INTO movie_likes VALUES", [(user_id, movie_id, rating, ts)])
    return ts


def is_like_visible(user_id, movie_id):
    result = client.execute(
        """
        SELECT count()
        FROM movie_likes
        WHERE user_id = %(u)s AND movie_id = %(m)s
        """,
        {"u": user_id, "m": movie_id},
    )
    return result[0][0] > 0


def measure_visibility(user_id, movie_id, rating):
    write_ts = insert_like(user_id, movie_id, rating)

    start = time.time()
    while time.time() - start < TIMEOUT:
        if is_like_visible(user_id, movie_id):
            return (time.time() - write_ts) * 1000
        time.sleep(POLL_INTERVAL)

    return None  # timeout


def run_test(n=1000):
    latencies = []

    for i in range(n):
        latency = measure_visibility(user_id=1000 + i, movie_id=42, rating=8)
        if latency is not None:
            latencies.append(latency)

    return latencies
