import sys
import os
import copy
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGO_URI
from utils.logging import log
from task_queue_module.crawl_task import crawl_product  # ✅ doc 단위로 처리

# ✅ 상위 경로에서 모듈 인식
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def convert_objectid_to_str(obj):
    """doc 내부 ObjectId → str 로 재귀 변환"""
    if isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(v) for v in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

def listen_for_changes():
    client = MongoClient(MONGO_URI)
    db = client["damoa"]

    target_collections = ["kakao_product", "naver_product"]

    pipeline = [
        {
            "$match": {
                "operationType": "insert",
                "ns.coll": {"$in": target_collections},
            }
        }
    ]

    try:
        with db.watch(pipeline) as stream:
            log.info("🔔 MongoDB change stream 감지 시작",
                     extra={"collections": target_collections})

            for change in stream:
                coll_name = change["ns"]["coll"]
                doc_raw   = change["fullDocument"]
                doc_id    = str(doc_raw["_id"])

                # ✅ ObjectId → str 변환
                doc_safe = convert_objectid_to_str(copy.deepcopy(doc_raw))

                log.info("📥 새 document 감지됨",
                         extra={"collection": coll_name, "doc_id": doc_id})

                if not doc_safe.get("products"):
                    log.warning("⚠️ products가 비어 있음",
                                extra={"collection": coll_name, "doc_id": doc_id})
                    continue

                log.info("🚀 전체 문서 단위 크롤링 태스크 전송",
                         extra={"collection": coll_name, "doc_id": doc_id})

                # ✅ 최종적으로 Celery에 안전하게 전송
                crawl_product.delay(doc_id, doc_safe)

    except PyMongoError:
        log.exception("❌ MongoDB change stream 오류")

if __name__ == "__main__":
    listen_for_changes()
