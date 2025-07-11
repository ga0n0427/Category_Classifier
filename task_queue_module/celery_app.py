from celery import Celery
from config import REDIS_URL

celery = Celery("category_tasks", broker=REDIS_URL, backend=REDIS_URL)
celery.autodiscover_tasks(['task_queue_module'])

# ✅ 이거 꼭 넣어야 crawl_task 내부 함수가 등록됨
import task_queue_module.crawl_task
import task_queue_module.infer_task