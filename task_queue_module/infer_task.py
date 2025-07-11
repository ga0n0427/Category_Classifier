from task_queue_module.celery_app import celery
from crawler.utils import preprocess_row_dict, preprocess_fallback_title_only
from model.classify import predict_category
from db.mongo_handler import save_final_document
from sentence_transformers import SentenceTransformer
import numpy as np
import multiprocessing as mp
import torch
import torch.multiprocessing

# 전역에서 모델 로드하지 않기
# model = SentenceTransformer(abs_path)  # 이 부분 제거

# 모델을 태스크 내부에서 로드
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        abs_path = "/home/gaon/gaon/final_project/category_classifier_project/saved_models/KoSimCSE"
        _model_cache = SentenceTransformer(abs_path)
        print("모델 로드 완료!")
    return _model_cache

@celery.task(queue="inference_queue", bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3}, retry_backoff=True)
def process_inference(self, doc_id: str, doc: dict):
    try:
        print(f"🚀 [inference-task] started: {doc_id}")
        
        # 태스크 시작 시 모델 로드
        model = get_model()
        
        # 1. 모든 product 분류
        for i, product in enumerate(doc.get("products", [])):
            crawled = product.get("crawled")
            if crawled:
                text = preprocess_row_dict(crawled)
            else:
                text = preprocess_fallback_title_only(product)
            print(f"🧠 product {i} 텍스트:", text)
            
            try:
                category = predict_category(text)
                print(f"✅ product {i} 예측 성공: {category}")
                doc["products"][i]["Category"] = category
            except Exception as e:
                print(f"❌ product {i} 예측 실패: {e}")
                doc["products"][i]["Category"] = "기타"

        # 2. 임베딩 생성
        title = doc.get("title", "")
        seller = doc.get("seller", "")
        product_names = " ".join(p.get("name", "") for p in doc["products"])
        categories = " ".join(p.get("Category", "") for p in doc["products"])
        full_text = f"{title} {seller} {product_names} {categories}"

        print("🧠 임베딩 텍스트:", full_text)

        try:
            embedding = model.encode(full_text, convert_to_numpy=True)
            embedding /= np.linalg.norm(embedding) + 1e-9
            doc["embedding"] = embedding.tolist()
            print(f"✅ 임베딩 생성 완료: {doc_id}")
        except Exception as e:
            print(f"❌ 임베딩 실패: {e}")
            doc["embedding"] = "12123"  # fallback

        # 4. 최종 문서 저장
        save_final_document(doc_id, doc)
        print(f"✅ 분류 및 임베딩 완료: {doc_id}")

    except Exception as e:
        print(f"❌ process_inference 실패: {e}")
        raise e