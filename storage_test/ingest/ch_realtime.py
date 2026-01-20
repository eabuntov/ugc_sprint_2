import time
from clickhouse_driver import Client

client = Client(
    host="clickhouse",
    database="analytics",
    user="benchmark",
    password="benchmark"
)

def insert_like(event):
    client.execute(
        "INSERT INTO movie_likes VALUES",
        [(event["user_id"], event["movie_id"],
          event["rating"], event["created_at"])]
    )

while True:
    event = get_next_event()  # generator / kafka / socket
    insert_like(event)
