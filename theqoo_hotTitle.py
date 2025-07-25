from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 옵션 설정 (브라우저 창 안 띄우려면 headless)
chrome_options = Options()
chrome_options.add_argument("--headless")  # 원하면 주석 처리

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    url = "https://theqoo.net/hot?filter_mode=normal&page=2"
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기

    # 1. class="hide_notice" 아래의 tr들 찾기
    hide_notice = driver.find_element(By.CLASS_NAME, "hide_notice")
    trs = hide_notice.find_elements(By.TAG_NAME, "tr")

    result = []
    for tr in trs:
        try:
            # 2. 각 tr의 td.title > a 태그 찾기
            td_title = tr.find_element(By.CLASS_NAME, "title")
            a_tag = td_title.find_element(By.TAG_NAME, "a")
            title = a_tag.text.strip()
            link = a_tag.get_attribute("href")
            result.append({"title": title, "link": link})
        except Exception:
            continue  # 해당 tr에 title이 없으면 패스

    # 결과 출력 (예시: 10개만)
    for idx, item in enumerate(result[5:20], 1):
        print(f"{idx}. {item['title']} ({item['link']})")

finally:
    driver.quit()
