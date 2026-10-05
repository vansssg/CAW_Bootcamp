import os

import redis as redis_client
from psycopg import connect


redis_url = os.environ["REDIS_URL"]
database_url = os.environ["DATABASE_URL"]

r = redis_client.from_url(redis_url, decode_responses=True)
conn = connect(database_url)


def process_job(link_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO analytics (link_id, timestamp_bucket, count, last_accessed_at)
            VALUES (%s, DATE_TRUNC('hour', NOW()), 1, NOW())
            ON CONFLICT (link_id, timestamp_bucket)
            DO UPDATE SET count = analytics.count + 1, last_accessed_at = NOW()
            """,
            (link_id,),
        )
        conn.commit()


if __name__ == "__main__":
    print("worker: started")
    while True:
        job = r.brpop("analytics:queue", timeout=5)
        if job:
            _, link_id = job
            process_job(link_id)
