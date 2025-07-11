import threading
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ✅ 크롬 드라이버 생성 함수
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver

# ✅ gift.kakao.com 크롤링 함수
def parse_gift(url: str, index: int):
    driver = create_driver()
    try:
        print(f"🧪 [Thread-{index}] 시작: {url}")
        driver.get(url + "?tab=detail")
        time.sleep(1)

        try:
            tab_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#tabPanel_detail > strong > a"))
            )
            driver.execute_script("arguments[0].click();", tab_button)
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠️ [Thread-{index}] 탭 클릭 실패: {e}")

        name = driver.find_element(By.CSS_SELECTOR, "#mArticle .product_subject h2").text.strip()
        price_raw = driver.find_element(By.CSS_SELECTOR, "#mArticle .wrap_priceinfo span").text.strip()
        price = price_raw.replace("\n", "").replace("원", "").strip()
        brand = driver.find_element(By.CSS_SELECTOR, "#mArticle .wrap_brand span.txt_shopname").text.strip()

        detail_info = {'브랜드': brand}
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
                print(f"⚠️ [Thread-{index}] 행 파싱 실패: {e}")

        result = {
            "Product_Name": name,
            "Price": price,
            "Category": "없음",
            "Detail_Info": json.dumps(detail_info, ensure_ascii=False)
        }
        print(f"🎯 [Thread-{index}] 결과:\n", json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ [Thread-{index}] 크롤링 실패: {e}")
    finally:
        driver.quit()

# ✅ 병렬 실행 함수
def run_threads():
    urls = [
        "https://gift.kakao.com/product/11239304",
        "https://gift.kakao.com/product/10101530",
        "https://gift.kakao.com/product/8829103",
        "https://gift.kakao.com/product/10979012",
        "https://gift.kakao.com/product/10201617",
        "https://gift.kakao.com/product/9572523"
    ]

    threads = []
    for i, url in enumerate(urls):
        t = threading.Thread(target=parse_gift, args=(url, i + 1))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    run_threads()
