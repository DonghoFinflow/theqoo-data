from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)


def crawl_theqoo(url, max_comments=20):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get(url)
        try:
            # 본문 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'oembedall-container'))
            )
            # 본문 추출
            try:
                content_element = driver.find_element(By.CLASS_NAME, 'xe_content')
                article_content = content_element.text.strip()
            except Exception:
                article_content = ""
        except Exception:
            article_content = ""

        # 댓글 더보기 클릭(최대 2회)
        for _ in range(2):
            try:
                more_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "show_more"))
                )
                more_button.click()
                time.sleep(1)
            except:
                break

        # 댓글 추출
        comments = driver.find_elements(By.CSS_SELECTOR, "ul.fdb_lst_ul > li")
        comment_texts = []
        for comment in comments[:max_comments]:
            try:
                comment_text = comment.find_element(By.CSS_SELECTOR, "div.xe_content").text.strip()
                comment_texts.append(comment_text)
            except:
                continue

        # 작성일시 추출
        # div.side.fr 요소가 로드될 때까지 대기
        wait = WebDriverWait(driver, 10)
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.side.fr")))

        # 그 안의 span 태그 텍스트 추출
        span = container.find_element(By.TAG_NAME, "span")

        # 1) 제목 추출: div.title
        title_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.title"))
        )
        title = title_elem.text.strip()

        return article_content, comment_texts, span.text, title
    finally:
        driver.quit()


@app.route('/theqoo-crawl', methods=['POST'])
def theqoo_crawl():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "url 필드가 필요합니다."}), 400

    article_content, comment_texts, article_date, title = crawl_theqoo(url)
    if not article_content:
        article_content = "게시글이 없습니다"

    # 댓글 한줄로 합치기(띄어쓰기로 구분)
    comments_joined = " ".join(comment_texts)

    # 게시글과 댓글 합치기
    llm_input = f"{title} {article_content} {comments_joined}".strip()

    return jsonify({
        "llm_input": llm_input,
        "article": article_content,
        "comments": comments_joined,
        "date": article_date,
        "title": title,
        "url": url
    })

@app.route('/trends', methods=['GET'])
def get_trends():
    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    # WebDriver 설정
    service = Service('/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://trends.google.co.kr/trending?geo=KR&sort=recency")

        # 동적 콘텐츠 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mZ3RIc"))
        )
        time.sleep(5)

        # 데이터 스크래핑
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        trends = []

        for item in soup.select('div.mZ3RIc'):
            # title = item.select_one('span.title').text.strip()
            # analysis = item.select_one('div.trend-analysis').text.strip() if item.select_one('div.trend-analysis') else 'N/A'
            # time_info = item.select_one('div.time-info').text.strip() if item.select_one('div.time-info') else 'N/A'

            trends.append({
                'Title': item.get_text(),
                # 'Analysis': analysis,
                # 'Time': time_info
            })

        return jsonify(trends)

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
