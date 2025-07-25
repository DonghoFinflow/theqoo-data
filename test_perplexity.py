#!/usr/bin/env python3
"""
Perplexity API 테스트 스크립트
"""

from perplexity import analyze_with_perplexity

def test_perplexity_analysis():
    """Perplexity 분석 함수 테스트"""
    
    # 테스트 데이터
    test_cases = [
        {
            "title": "최신 아이폰 출시 소식",
            "content": "애플에서 새로운 아이폰을 출시했다는 소식이 전해졌습니다.",
            "comments": [
                "정말 기대되네요!",
                "가격이 너무 비싸지 않을까?",
                "새로운 기능이 궁금해요"
            ]
        },
        {
            "title": "날씨가 너무 덥다",
            "content": "요즘 날씨가 정말 덥네요. 에어컨 없이는 살 수 없을 것 같습니다.",
            "comments": [
                "정말 덥죠...",
                "비라도 와야겠어요",
                "가을이 빨리 와야겠어요"
            ]
        }
    ]
    
    print("=== Perplexity API 테스트 시작 ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 테스트 케이스 {i} ---")
        print(f"제목: {test_case['title']}")
        print(f"본문: {test_case['content']}")
        print(f"댓글: {test_case['comments']}")
        print("\n분석 결과:")
        
        try:
            result = analyze_with_perplexity(
                test_case['title'], 
                test_case['content'], 
                test_case['comments']
            )
            print(result)
        except Exception as e:
            print(f"오류 발생: {e}")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_perplexity_analysis() 