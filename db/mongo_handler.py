#mongo_handler.py
from pymongo import MongoClient, errors
from pymongo.errors import PyMongoError
from bson import ObjectId
from config import MONGO_URI
from utils.logging import log

def save_classified_product(doc_id: str, product: dict, category: str):
    """
    분류 결과(category)를 기존 MongoDB 문서의 products 항목 중 해당 product에 추가하는 함수
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client["damoa"]

        # 업데이트 대상 컬렉션 추정: 원본 문서 저장소
        target_collections = ["kakao_product", "naver_product"]

        updated = False
        for coll_name in target_collections:
            collection = db[coll_name]

            result = collection.update_one(
                {"_id": ObjectId(doc_id), "products.link": product.get("link")},
                {"$set": {"products.$.Category": category}}
            )

            if result.modified_count > 0:
                updated = True
                log.info("✅ 분류 결과 저장 완료", extra={
                    "doc_id": doc_id,
                    "link": product.get("link"),
                    "category": category,
                    "collection": coll_name
                })
                break

        if not updated:
            log.warning("⚠️ 업데이트된 문서 없음", extra={
                "doc_id": doc_id,
                "link": product.get("link")
            })

    except PyMongoError as e:
        log.exception(f"❌ MongoDB 업데이트 중 오류 발생: {e}")
    finally:
        client.close()

def save_final_document(doc_id: str, full_doc: dict):
    """
    모든 Category·embedding 처리가 끝난 doc을 한 번에 저장하되,
    immutable 필드 '_id' 는 제외하고 $set 한다.
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client["damoa"]

        # _id 제거한 사본
        doc_no_id = {k: v for k, v in full_doc.items() if k != "_id"}

        # 🔍 저장할 문서 내용 출력
        print(f"\n📄 저장 대상 문서 (doc_id: {doc_id}):")
        for k, v in doc_no_id.items():
            print(f" - {k}: {str(v)[:200]}")  # 길이 제한으로 앞부분만

        for coll in ["kakao_product", "naver_product"]:
            result = db[coll].update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": doc_no_id}
            )
            if result.modified_count:
                log.info("✅ 전체 문서 저장 완료",
                         extra={"doc_id": doc_id, "collection": coll})
                print(f"✅ 전체 문서 저장 완료 → {coll}")
                break
        else:
            log.warning("⚠️ 전체 문서 저장 실패: 대상 없음",
                        extra={"doc_id": doc_id})
            print("⚠️ 대상 문서 없음 → 저장 실패")

    except errors.PyMongoError as e:
        log.exception("❌ 전체 문서 저장 중 오류 발생: %s", e)
        print(f"❌ MongoDB 오류 발생: {e}")
    finally:
        client.close()