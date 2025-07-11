# crawl_task.py

from task_queue_module.celery_app import celery
from crawler.fetch_html import create_driver
from crawler.dispatcher import route_to_parser
from task_queue_module.infer_task import process_inference

@celery.task(queue="crawl_queue", bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3}, retry_backoff=True)
def crawl_product(self, doc_id: str, doc: dict):
    """
    doc 안의 모든 product를 크롤링하고, 결과를 각 product에 추가한 후
    다음 단계 태스크로 완성된 doc을 넘김
    """
    driver = create_driver()
    try:
        for idx, product in enumerate(doc.get("products", [])):
            url = product.get("link")
            if not url:
                continue

            try:
                result = route_to_parser(url, driver)
                doc["products"][idx]["crawled"] = result  # ✅ 크롤링 결과 저장
            except Exception as e:
                print(f"❌ product {idx} 크롤링 실패: {url} → {e}")

        # ✅ 다음 단계로 완성된 doc 전달
        process_inference.delay(doc_id, doc)

    except Exception as e:
        print(f"❌ crawl_product 전체 실패: {e}")
        raise e

    finally:
        driver.quit()
