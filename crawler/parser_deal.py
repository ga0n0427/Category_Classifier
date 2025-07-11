from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from utils.logging import log

def parse_deal(url: str, driver):
    try:
        driver.get(url)

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "#mArticle > div > div.product_section > app-view-product-category-path > div > div > a"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 카테고리
        elements = soup.select("#mArticle > div > div.product_section > app-view-product-category-path > div > div > a")
        category_texts = [el.text.strip() for el in elements]
        category = " > ".join(category_texts) if category_texts else "없음"

        # 상품명
        name_el = soup.select_one("#mArticle .box_prdinfo strong span span")
        name = name_el.text.strip() if name_el else "없음"

        # 가격
        price_el = soup.select_one("#mArticle .txt_price")
        price = price_el.text.strip().replace("원", "").replace(",", "") if price_el else "없음"

        # ✅ gift 형식에 맞춰 반환
        return {
            "Product_Name": name,
            "Price": price,
            "Category": "없음",
            "Detail_Info": json.dumps({"카테고리": category}, ensure_ascii=False)
        }

    except Exception as e:
        log.exception("❌ store.kakao 크롤링 실패", extra={"url": url})
        return None