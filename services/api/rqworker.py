import os
import django
from redis import Redis
from rq import Worker, Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keelshift_api.settings")
django.setup()

redis_conn = Redis.from_url(os.environ["REDIS_URL"])
queue = Queue(connection=redis_conn)  # default queue

worker = Worker([queue], connection=redis_conn)
worker.work(with_scheduler=False)
