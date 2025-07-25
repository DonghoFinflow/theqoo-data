from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_post_datetime(url):
    # Chrome 옵션 설정 (headless 모드)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # div.side.fr 요소가 로드될 때까지 대기
        wait = WebDriverWait(driver, 10)
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.side.fr")))

        # 그 안의 span 태그 텍스트 추출
        span = container.find_element(By.TAG_NAME, "span")
        return span.text

    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://theqoo.net/hot/3746707400"
    datetime_str = fetch_post_datetime(url)
    if datetime_str:
        print("작성일과 시간:", datetime_str)
    else:
        print("작성일시 정보를 찾을 수 없습니다.")
