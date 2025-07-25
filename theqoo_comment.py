from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 사용 시
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 드라이버 초기화
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

try:
    # 1. 게시글 접속
    url = 'https://theqoo.net/hot/3746707400?filter_mode=normal&page=31'
    driver.get(url)
    try:

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'oembedall-container')))  # 본문 로딩 대기

        # 2. 본문 내용 추출
        content_element = driver.find_element(By.CLASS_NAME, 'xe_content')
        article_content = content_element.text.strip()
        print(f"=== 게시글 내용 ===\n{article_content}\n")

    except Exception as e:
        print("본문을 찾지 못했습니다:", e)

    # 3. 댓글 더보기 클릭 (최대 100개까지)
    comment_count = 0
    max_comments = 30

    print("버튼 클릭 전")
    # 첫 번째 클릭 시도
    try:
        more_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "show_more"))
        )
        more_button.click()
        time.sleep(1)  # 댓글 로딩 대기

        # 두 번째 클릭 시도 (버튼이 있으면 클릭, 없으면 패스)
        try:
            more_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "show_more"))
            )
            more_button.click()
            time.sleep(1)
        except:
            # 두 번째 버튼이 없으면 그냥 넘어감
            pass

    except Exception as e:
        print("버튼을 찾지 못했습니다:", e)

    # 수정된 댓글 추출 부분
    comments = driver.find_elements(By.CSS_SELECTOR, "ul.fdb_lst_ul > li")  # li 요소 선택
    for idx, comment in enumerate(comments[:max_comments], 1):
        try:
            # li 안에서 댓글 텍스트 추출 (상대 선택자 사용)
            comment_text = comment.find_element(By.CSS_SELECTOR, "div.xe_content").text.strip()
            if "비회원" in comment_text:
                print("비회원용")
            print(f"[{idx}번 댓글] {comment_text}")
        except:
            print(f"[{idx}번 댓글] 추출 실패")

finally:
    driver.quit()
