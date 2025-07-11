import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_naver(url: str, driver):
    try:
        print(f"🔍 접속 시도: {url}")
        driver.get(url)
        time.sleep(2)

        detail_info = {}

        # ✅ 초기 버튼 클릭 시도 (상품정보 열기 버튼)
        try:
            info_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#DEFAULT > div > div._13zS-8ytsi > div._2uebWEwMtD._2KAAPQAtvq > button"))
            )
            driver.execute_script("arguments[0].click();", info_button)
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠️ 상품정보 버튼 클릭 실패: {e}")

        # ✅ 상품 상세 span과 div 가져오기
        try:
            span_elements = driver.find_elements(By.CSS_SELECTOR, "#DEFAULT > div > div._13zS-8ytsi > div._2uebWEwMtD > ul > li > span")
            div_elements = driver.find_elements(By.CSS_SELECTOR, "#DEFAULT > div > div._13zS-8ytsi > div._2uebWEwMtD > ul > li > div")

            for span, div in zip(span_elements, div_elements):
                key = span.text.strip()
                value = div.text.strip()
                if key and value:
                    detail_info[key] = value
        except Exception as e:
            print(f"⚠️ 상세정보 추출 실패: {e}")

        # ✅ 상품명 (title)
        try:
            name = driver.find_element(By.CSS_SELECTOR, "#content > div:nth-child(1) > div > div._2KN9hCjYFh > div:nth-child(1) > h3 > span").text.strip()
        except:
            name = "없음"

        # ✅ 가격
        try:
            price_raw = driver.find_element(By.CSS_SELECTOR, "span._1LY7DqCnwR").text.strip()
            price = price_raw.replace("\n", "").replace("원", "").strip()
        except:
            price = "없음"

        print("✅ 크롤링 완료:", detail_info)

        return {
            "Product_Name": name,
            "Price": price,
            "Category": "없음",
            "Detail_Info": json.dumps(detail_info, ensure_ascii=False),
            "url": url,
        }

    except Exception as e:
        print(f"❌ parse_naver 크롤링 실패: {e}")
        return {
            "Product_Name": "없음",
            "Price": "없음",
            "Category": "없음",
            "Detail_Info": "{}",
            "url": url
        }
