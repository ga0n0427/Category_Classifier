# crawler/utils.py
import json

excluded_values = ['해당없음', '상세', '해당사항', '판매원', '인증', '번호', '기타']
excluded_keys = ['소비자 상담 관련 전화번호', 'A/S', '원산지', '제조', '품질', '에너지', '통신판매', '청약철회']
from urllib.parse import urlparse, urlunparse

def clean_gift_url(url: str) -> str:
    """❗ 불필요한 쿼리 제거 후 ?tab=detail 붙이기"""
    parsed = urlparse(url)
    cleaned = parsed._replace(query="")  # 쿼리 제거
    return urlunparse(cleaned) + "?tab=detail"

def preprocess_row_dict(row: dict) -> str:
    # ✅ 제품명, 가격, 상세 정보(raw JSON 문자열)를 각각 추출
    product_name = str(row.get('Product_Name', '')).strip()
    price = str(row.get('Price', '')).strip()
    detail_info_raw = str(row.get('Detail_Info', '')).strip()

    try:
        # ✅ JSON 형식의 상세 정보를 파싱
        detail_info = json.loads(detail_info_raw)
        filtered_details = []

        # ✅ 필터링 기준에 따라 유의미한 정보만 추출
        for key, value in detail_info.items():
            # ❌ 값이 제외 목록(excluded_values)에 포함되면 스킵
            if any(ex in value for ex in excluded_values):
                continue
            # ❌ 키가 제외 목록(excluded_keys)에 포함되면 스킵
            if any(ex in key for ex in excluded_keys):
                continue
            # ✅ key: value 형태로 저장
            filtered_details.append(f"{key}: {value}")

        # ✅ 필터링된 상세 정보들을 슬래시(/)로 구분해 하나의 문자열로 결합
        detail_text = " / ".join(filtered_details)

    except Exception:
        # ⚠️ JSON 파싱 실패 시, 원본 문자열을 그대로 사용
        detail_text = detail_info_raw

    # ✅ 최종 출력 포맷: [TITLE] 제품명 [INFO] 가격 및 상세 정보
    return f"[TITLE] {product_name} [INFO] 가격: {price}원" + (f" / {detail_text}" if detail_text else "")

def preprocess_fallback_title_only(product: dict) -> str:
    name = str(product.get("name", "")).strip()
    return f"[TITLE] {name} [INFO]"
