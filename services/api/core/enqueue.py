import os
from redis import Redis
from rq import Queue
from core.jobs import process_run

def enqueue_run(run_id: int) -> str:
    redis_conn = Redis.from_url(os.environ["REDIS_URL"])
    job = Queue(connection=redis_conn).enqueue(process_run, run_id)
    return job.id