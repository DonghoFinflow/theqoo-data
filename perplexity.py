import os
import requests
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def analyze_with_perplexity(title, content="", comments=None):
    """
    Perplexity API를 사용하여 제목과 댓글을 분석
    
    Args:
        title (str): 게시글 제목
        content (str): 게시글 본문 내용 (선택사항)
        comments (list): 댓글 리스트 (선택사항)
    
    Returns:
        str: Perplexity API 분석 결과
    """
    # 환경변수에서 API 키 가져오기
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다.")
    
    url = "https://api.perplexity.ai/chat/completions"
    
    # 댓글을 하나의 텍스트로 결합
    if comments and isinstance(comments, list):
        comments_text = "\n".join(comments)
    else:
        comments_text = "댓글이 없습니다."
    
    # 전체 내용 구성
    full_content = f"제목: {title}\n\n"
    if content:
        full_content += f"본문: {content}\n\n"
    full_content += f"댓글:\n{comments_text}"
    
    # 프롬프트와 시스템 메시지 구성
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "상세한 설명과 함께 반드시 출처를 인용해 답변하세요."},
            {"role": "user", "content": f"이 제목과 댓글을 읽고 최근에 관련 내용의 기사와 이벤트를 찾아서 요약 정리 해줘\n\n{full_content}"}
        ],
        "max_tokens": 800,
        "temperature": 0.5
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get("choices"):
            return result["choices"][0]["message"]["content"]
        else:
            return "분석 결과를 가져올 수 없습니다."
            
    except Exception as e:
        return f"분석 중 오류 발생: {e}"

def main():
    """테스트용 메인 함수"""
    # 테스트 데이터
    test_title = "테스트 제목"
    test_content = "테스트 본문 내용입니다."
    test_comments = [
        "첫 번째 댓글입니다.",
        "두 번째 댓글입니다.",
        "세 번째 댓글입니다."
    ]
    
    print("=== Perplexity API 테스트 ===")
    print(f"제목: {test_title}")
    print(f"본문: {test_content}")
    print(f"댓글: {test_comments}")
    print("\n=== 분석 결과 ===")
    
    result = analyze_with_perplexity(test_title, test_content, test_comments)
    print(result)

if __name__ == "__main__":
    main()


