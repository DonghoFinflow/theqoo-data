from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 백그라운드 실행
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

# WebDriver 경로 설정 (ChromeDriver 경로 입력 필요)
service = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://trends.google.co.kr/trending?geo=KR&sort=recency")

    # 동적 콘텐츠 로딩 대기 (최대 15초)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.mZ3RIc"))
    )

    # 추가 로딩 시간 확보
    time.sleep(5)

    # 페이지 소스 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    trends = []

    # 트렌드 아이템 추출
    for item in soup.select('div.mZ3RIc'):
        # print(item)
        # title = item.select_one('div.mZ3RIc').text.strip()
        # analysis = item.select_one('div.trend-analysis').text.strip() if item.select_one(
        #     'div.trend-analysis') else 'N/A'
        # time_info = item.select_one('div.time-info').text.strip() if item.select_one('div.time-info') else 'N/A'
        #
        trends.append({
            'Title': item.get_text(),
            # 'Analysis': analysis,
            # 'Time': time_info
        })

    # DataFrame으로 변환
    df = pd.DataFrame(trends)
    print(df)

finally:
    driver.quit()
