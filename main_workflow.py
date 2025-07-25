import os
import json
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TheqooWorkflow:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    def get_hot_titles(self, page_num=2, start_idx=5, end_idx=20):
        """theqoo에서 핫타이틀 수집"""
        logger.info(f"페이지 {page_num}에서 핫타이틀 수집 시작")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        result = []
        
        try:
            url = f"https://theqoo.net/hot?filter_mode=normal&page={page_num}"
            driver.get(url)
            time.sleep(3)
            
            hide_notice = driver.find_element(By.CLASS_NAME, "hide_notice")
            trs = hide_notice.find_elements(By.TAG_NAME, "tr")
            
            for tr in trs:
                try:
                    td_title = tr.find_element(By.CLASS_NAME, "title")
                    a_tag = td_title.find_element(By.TAG_NAME, "a")
                    title = a_tag.text.strip()
                    link = a_tag.get_attribute("href")
                    result.append({"title": title, "link": link})
                except Exception as e:
                    logger.debug(f"제목 추출 실패: {e}")
                    continue
            
            # 지정된 범위의 결과만 반환
            return result[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"핫타이틀 수집 실패: {e}")
            return []
        finally:
            driver.quit()
    
    def classify_titles(self, titles_data):
        """Perplexity API를 사용하여 정치 관련 여부 분류"""
        logger.info("제목 분류 시작")
        
        if not titles_data:
            return []
        
        prompt = (
            "다음은 인터넷 게시판의 게시글 제목 목록입니다.\n"
            "각 제목이 정치 관련(정치, 선거, 정당, 정부, 정치인 등) 게시글인지 아닌지 판단해주세요.\n"
            "정치 관련이면 'N', 정치가 아니면 유머/이슈 등으로 'Y'로 표시해주세요.\n"
            "아래와 같은 JSON 리스트 형태로 결과를 반환하세요:\n"
            "[{\"title\": 제목, \"link\": 링크, \"is_issue\": \"Y 또는 N\"}, ...]\n\n"
            "제목 목록:\n"
        )
        
        for item in titles_data:
            prompt += f"- {item['title']} - {item['link']}\n"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
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
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                output_json = response.json()["choices"][0]["message"]["content"]
                output_list = json.loads(output_json)
                logger.info(f"분류 완료: {len(output_list)}개 항목")
                return output_list
            else:
                logger.error(f"Perplexity API 호출 실패: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"분류 중 오류: {e}")
            return []
    
    def get_post_datetime(self, url):
        """게시글 작성일시 추출"""
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.side.fr")))
            span = container.find_element(By.TAG_NAME, "span")
            return span.text
        except Exception as e:
            logger.error(f"작성일시 추출 실패: {e}")
            return None
        finally:
            driver.quit()
    
    def get_post_content_and_comments(self, url, max_comments=30):
        """게시글 내용과 댓글 수집"""
        logger.info(f"게시글 내용 및 댓글 수집: {url}")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        
        try:
            driver.get(url)
            
            # 본문 내용 추출
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'xe_content')))
                content_element = driver.find_element(By.CLASS_NAME, 'xe_content')
                article_content = content_element.text.strip()
            except Exception as e:
                logger.warning(f"본문 추출 실패: {e}")
                article_content = ""
            
            # 댓글 더보기 클릭
            try:
                more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "show_more"))
                )
                more_button.click()
                time.sleep(1)
                
                # 두 번째 클릭 시도
                try:
                    more_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "show_more"))
                    )
                    more_button.click()
                    time.sleep(1)
                except:
                    pass
            except Exception as e:
                logger.debug(f"댓글 더보기 버튼 클릭 실패: {e}")
            
            # 댓글 추출
            comments = []
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "ul.fdb_lst_ul > li")
            
            for idx, comment in enumerate(comment_elements[:max_comments], 1):
                try:
                    comment_text = comment.find_element(By.CSS_SELECTOR, "div.xe_content").text.strip()
                    if comment_text and "비회원" not in comment_text:
                        comments.append(comment_text)
                except Exception as e:
                    logger.debug(f"댓글 {idx} 추출 실패: {e}")
            
            return {
                "content": article_content,
                "comments": comments
            }
            
        except Exception as e:
            logger.error(f"게시글 수집 실패: {e}")
            return {"content": "", "comments": []}
        finally:
            driver.quit()
    
    def analyze_with_perplexity(self, title, content, comments):
        """Perplexity API로 제목과 댓글 분석"""
        logger.info(f"Perplexity 분석 시작: {title[:30]}...")
        
        try:
            # perplexity.py의 함수 사용
            from perplexity import analyze_with_perplexity
            return analyze_with_perplexity(title, content, comments)
        except Exception as e:
            logger.error(f"Perplexity 분석 실패: {e}")
            return f"분석 중 오류 발생: {e}"
    
    def run_workflow(self, page_num=2, start_idx=5, end_idx=15):
        """전체 워크플로우 실행"""
        logger.info("=== Theqoo 워크플로우 시작 ===")
        
        # 1. 핫타이틀 수집
        titles = self.get_hot_titles(page_num, start_idx, end_idx)
        if not titles:
            logger.error("핫타이틀 수집 실패")
            return []
        
        logger.info(f"수집된 제목 수: {len(titles)}")
        
        # 2. 정치 관련 여부 분류
        classified_titles = self.classify_titles(titles)
        if not classified_titles:
            logger.error("제목 분류 실패")
            return []
        
        # 3. 정치가 아닌 이슈만 필터링
        issue_titles = [item for item in classified_titles if item.get("is_issue") == "Y"]
        logger.info(f"이슈로 분류된 제목 수: {len(issue_titles)}")
        
        # 4. 각 이슈에 대해 상세 정보 수집
        documents = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for idx, item in enumerate(issue_titles, 1):
            logger.info(f"처리 중: {idx}/{len(issue_titles)} - {item['title'][:30]}...")
            
            try:
                # 작성일시 추출
                post_datetime = self.get_post_datetime(item['link'])
                
                # 게시글 내용과 댓글 수집
                post_data = self.get_post_content_and_comments(item['link'])
                
                # Perplexity 분석
                analysis = self.analyze_with_perplexity(
                    item['title'], 
                    post_data['content'], 
                    post_data['comments']
                )
                
                # 문서 생성
                document = {
                    "title": item['title'],
                    "link": item['link'],
                    "post_datetime": post_datetime,
                    "content": post_data['content'],
                    "comments": post_data['comments'],
                    "comments_count": len(post_data['comments']),
                    "analysis": analysis,
                    "collected_date": current_date,
                    "id": f"theqoo_{current_date}_{idx}"
                }
                
                documents.append(document)
                logger.info(f"문서 생성 완료: {document['id']}")
                
                # API 호출 간격 조절
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"문서 처리 실패: {e}")
                continue
        
        logger.info(f"=== 워크플로우 완료: {len(documents)}개 문서 생성 ===")
        return documents
    
    def save_documents(self, documents, filename=None):
        """문서를 JSON 파일로 저장"""
        if not filename:
            current_date = datetime.now().strftime("%Y%m%d")
            filename = f"theqoo_documents_{current_date}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            logger.info(f"문서 저장 완료: {filename}")
            return filename
        except Exception as e:
            logger.error(f"문서 저장 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    workflow = TheqooWorkflow()
    
    # 워크플로우 실행
    documents = workflow.run_workflow(page_num=2, start_idx=5, end_idx=15)
    
    if documents:
        # 문서 저장
        saved_file = workflow.save_documents(documents)
        if saved_file:
            print(f"\n=== 완료 ===")
            print(f"생성된 문서 수: {len(documents)}")
            print(f"저장된 파일: {saved_file}")
            
            # 샘플 출력
            if documents:
                print(f"\n=== 샘플 문서 ===")
                sample = documents[0]
                print(f"제목: {sample['title']}")
                print(f"댓글 수: {sample['comments_count']}")
                print(f"분석 길이: {len(sample['analysis'])} 문자")
    else:
        print("문서 생성에 실패했습니다.")

if __name__ == "__main__":
    main() 