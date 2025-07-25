from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 크롬 옵션 설정 (브라우저 창 안 띄우려면 headless)
chrome_options = Options()
chrome_options.add_argument("--headless") # 필요시 주석 처리

# 환경변수에서 API 키 가져오기
api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    raise ValueError("PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다.")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    url = "https://theqoo.net/hot?filter_mode=normal&page=3"
    driver.get(url)
    time.sleep(3) # 페이지 로딩 대기

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
            continue # 해당 tr에 title이 없으면 패스

    # Perplexity API에 보낼 데이터 준비 (예시: 10개만)
    items = result[5:15]

    # Perplexity 프롬프트 작성
    prompt = (
        "다음은 인터넷 게시판의 게시글 제목 목록입니다.\n"
        "각 제목이 정치 관련(정치, 선거, 정당, 정부, 정치인 등) 게시글인지 아닌지 판단해주세요.\n"
        "정치 관련이면 'N', 정치가 아니면 유머/이슈 등으로 'Y'로 표시해주세요.\n"
        "아래와 같은 JSON 리스트 형태로 결과를 반환하세요:\n"
        "[{\"title\": 제목, \"link\": 링크, \"is_issue\": \"Y 또는 N\"}, ...]\n\n"
        "제목 목록:\n"
    )
    for item in items:
        prompt += f"- {item['title']} - {item['link']}\n"

    # Perplexity API 호출
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar",  # 최신 모델명
        "messages": [
            {
                "role": "system",
                "content": (
                    "당신은 정치 관련 여부를 분류하는 분류기입니다. "
                    "아래의 게시글 제목 리스트를 정치 관련이면 'N', 아니면 'Y'로 분류하고, "
                    "JSON 리스트만 반환하세요. 설명이나 기타 텍스트는 포함하지 마세요."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    # Perplexity 응답 파싱
    if response.status_code == 200:
        # Perplexity는 JSON 문자열만 반환하도록 프롬프트에 명시
        output_json = response.json()["choices"][0]["message"]["content"]
        # 문자열을 실제 리스트로 변환
        output_list = json.loads(output_json)
        print(json.dumps(output_list, ensure_ascii=False, indent=2))
    else:
        print("Perplexity API 호출 실패:", response.text)

finally:
    driver.quit()
