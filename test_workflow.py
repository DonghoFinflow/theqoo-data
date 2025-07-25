#!/usr/bin/env python3
"""
Main Workflow 테스트 스크립트 - 3개 제목만으로 테스트
"""

import logging
from main_workflow import TheqooWorkflow

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_workflow_with_3_titles():
    """3개의 제목만으로 워크플로우 테스트"""
    
    print("=== Main Workflow 테스트 시작 (3개 제목) ===")
    
    try:
        # 워크플로우 초기화
        workflow = TheqooWorkflow()
        
        # 1단계: 핫타이틀 수집 (3개만)
        print("\n1단계: 핫타이틀 수집...")
        titles = workflow.get_hot_titles(page_num=2, start_idx=5, end_idx=8)  # 3개만
        
        if not titles:
            print("❌ 핫타이틀 수집 실패")
            return False
        
        print(f"✅ {len(titles)}개 제목 수집 완료:")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title['title'][:50]}...")
        
        # 2단계: 정치 관련 여부 분류
        print("\n2단계: 제목 분류...")
        classified_titles = workflow.classify_titles(titles)
        
        if not classified_titles:
            print("❌ 제목 분류 실패")
            return False
        
        print(f"✅ {len(classified_titles)}개 제목 분류 완료")
        
        # 3단계: 정치가 아닌 이슈만 필터링
        issue_titles = [item for item in classified_titles if item.get("is_issue") == "Y"]
        print(f"✅ 이슈로 분류된 제목: {len(issue_titles)}개")
        
        if not issue_titles:
            print("⚠️ 이슈로 분류된 제목이 없습니다. 모든 제목을 처리합니다.")
            issue_titles = classified_titles
        
        # 4단계: 각 이슈에 대해 상세 정보 수집 (최대 3개)
        print(f"\n3단계: 상세 정보 수집 (최대 {min(3, len(issue_titles))}개)...")
        
        documents = []
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for idx, item in enumerate(issue_titles[:3], 1):  # 최대 3개만
            print(f"\n--- 처리 중: {idx}/{min(3, len(issue_titles))} ---")
            print(f"제목: {item['title'][:50]}...")
            
            try:
                # 작성일시 추출
                print("  - 작성일시 추출 중...")
                post_datetime = workflow.get_post_datetime(item['link'])
                print(f"    작성일시: {post_datetime}")
                
                # 게시글 내용과 댓글 수집
                print("  - 게시글 내용 및 댓글 수집 중...")
                post_data = workflow.get_post_content_and_comments(item['link'], max_comments=10)  # 댓글 10개만
                print(f"    댓글 수: {len(post_data['comments'])}개")
                
                # Perplexity 분석
                print("  - Perplexity 분석 중...")
                analysis = workflow.analyze_with_perplexity(
                    item['title'], 
                    post_data['content'], 
                    post_data['comments']
                )
                print(f"    분석 완료 (길이: {len(analysis)} 문자)")
                
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
                print(f"  ✅ 문서 생성 완료: {document['id']}")
                
                # API 호출 간격 조절
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"문서 처리 실패: {e}")
                print(f"  ❌ 오류: {e}")
                continue
        
        # 결과 출력
        print(f"\n=== 테스트 완료 ===")
        print(f"생성된 문서 수: {len(documents)}")
        
        if documents:
            print("\n=== 샘플 문서 ===")
            sample = documents[0]
            print(f"제목: {sample['title']}")
            print(f"링크: {sample['link']}")
            print(f"작성일시: {sample['post_datetime']}")
            print(f"댓글 수: {sample['comments_count']}")
            print(f"분석 길이: {len(sample['analysis'])} 문자")
            print(f"분석 미리보기: {sample['analysis'][:100]}...")
            
            # JSON 파일로 저장
            import json
            filename = f"test_documents_{current_date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            print(f"\n문서가 {filename}에 저장되었습니다.")
        
        return True
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        print(f"❌ 테스트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("Main Workflow 테스트를 시작합니다...")
    print("이 테스트는 3개의 제목만으로 전체 워크플로우를 검증합니다.\n")
    
    success = test_workflow_with_3_titles()
    
    if success:
        print("\n🎉 테스트 성공!")
    else:
        print("\n💥 테스트 실패!")

if __name__ == "__main__":
    main() 