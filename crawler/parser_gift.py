import json
from utils.logging import log
from .utils import clean_gift_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def parse_gift(url: str, driver):
    print("🧪 parse_gift 함수 실행됨")

    try:
        cleaned_url = clean_gift_url(url)
        driver.get(cleaned_url)
        time.sleep(1.5)  # 페이지 기본 로딩 대기

        # ✅ "상품고시정보" 탭 클릭 (존재할 경우만)
        try:
            tab_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#tabPanel_detail > strong > a"))
            )
            driver.execute_script("arguments[0].click();", tab_button)
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠️ 탭 클릭 실패 (JS): {e}")

        # 상품명
        name = driver.find_element(By.CSS_SELECTOR, "#mArticle .product_subject h2").text.strip()
        price_raw = driver.find_element(By.CSS_SELECTOR, "#mArticle .wrap_priceinfo span").text.strip()
        price = price_raw.replace("\n", "").replace("원", "").strip()

        # 브랜드
        brand = driver.find_element(By.CSS_SELECTOR, "#mArticle .wrap_brand span.txt_shopname").text.strip()
        detail_info = {'브랜드': brand}

        # ✅ 테이블 로드 대기 후 파싱
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.tbl_detail"))
        )
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl_detail tbody tr")
        for row in table_rows:
            try:
                key = row.find_element(By.TAG_NAME, "th").text.strip()
                value = row.find_element(By.TAG_NAME, "td").text.strip()
                if key and value:
                    detail_info[key] = value
            except Exception as e:
                print(f"⚠️ 행 파싱 실패: {e}")

        detail_json = json.dumps(detail_info, ensure_ascii=False)

        return {
            "Product_Name": name,
            "Price": price,
            "Category": "없음",
            "Detail_Info": detail_json
        }


    except Exception as e:
        log.exception(f"❌ gift.kakao 크롤링 실패: {e}")
        return None
