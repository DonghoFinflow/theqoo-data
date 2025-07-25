#!/usr/bin/env python3
"""
Hot 게시판 2~10페이지 데이터 수집 스크립트
테스트용 문서 생성을 위한 데이터 수집
"""

import logging
import json
import time
from datetime import datetime
from main_workflow import TheqooWorkflow

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_hot_pages_data():
    """Hot 게시판 2~10페이지 데이터 수집"""
    
    print("=== Hot 게시판 2~10페이지 데이터 수집 시작 ===")
    
    try:
        # 워크플로우 초기화
        workflow = TheqooWorkflow()
        
        all_titles = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 2~10페이지 순회
        for page_num in range(2, 11):
            print(f"\n📄 페이지 {page_num} 수집 중...")
            
            try:
                # 각 페이지에서 모든 제목 수집 (start_idx=0, end_idx=20으로 설정하여 모든 제목 가져오기)
                titles = workflow.get_hot_titles(page_num=page_num, start_idx=0, end_idx=20)
                
                if not titles:
                    print(f"⚠️ 페이지 {page_num}에서 제목을 가져올 수 없습니다.")
                    continue
                
                # 페이지 정보 추가
                for title in titles:
                    title['page_num'] = page_num
                    title['collected_date'] = current_date
                
                all_titles.extend(titles)
                print(f"✅ 페이지 {page_num}: {len(titles)}개 제목 수집 완료")
                
                # 페이지 간 간격 조절 (서버 부하 방지)
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"페이지 {page_num} 수집 실패: {e}")
                print(f"❌ 페이지 {page_num} 수집 실패: {e}")
                continue
        
        # 결과 출력
        print(f"\n=== 수집 완료 ===")
        print(f"총 수집된 제목 수: {len(all_titles)}")
        
        # 페이지별 통계
        page_stats = {}
        for title in all_titles:
            page_num = title['page_num']
            if page_num not in page_stats:
                page_stats[page_num] = 0
            page_stats[page_num] += 1
        
        print("\n📊 페이지별 수집 현황:")
        for page_num in sorted(page_stats.keys()):
            print(f"  페이지 {page_num}: {page_stats[page_num]}개")
        
        # JSON 파일로 저장
        filename = f"hot_pages_2_10_{current_date}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_titles, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 데이터가 {filename}에 저장되었습니다.")
        
        # 샘플 데이터 출력
        if all_titles:
            print("\n=== 샘플 데이터 ===")
            sample = all_titles[0]
            print(f"제목: {sample['title']}")
            print(f"링크: {sample['link']}")
            print(f"페이지: {sample['page_num']}")
            print(f"수집일: {sample['collected_date']}")
        
        return True, all_titles
        
    except Exception as e:
        logger.error(f"데이터 수집 중 오류 발생: {e}")
        print(f"❌ 데이터 수집 실패: {e}")
        return False, []

def create_test_documents(titles_data, max_documents=50):
    """수집된 제목 데이터로 테스트용 문서 생성"""
    
    print(f"\n=== 테스트용 문서 생성 시작 (최대 {max_documents}개) ===")
    
    try:
        workflow = TheqooWorkflow()
        documents = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 제목 분류
        print("1단계: 제목 분류 중...")
        classified_titles = workflow.classify_titles(titles_data[:max_documents])
        
        if not classified_titles:
            print("❌ 제목 분류 실패")
            return False, []
        
        print(f"✅ {len(classified_titles)}개 제목 분류 완료")
        
        # 이슈로 분류된 제목만 필터링
        issue_titles = [item for item in classified_titles if item.get("is_issue") == "Y"]
        print(f"✅ 이슈로 분류된 제목: {len(issue_titles)}개")
        
        if not issue_titles:
            print("⚠️ 이슈로 분류된 제목이 없습니다. 모든 제목을 처리합니다.")
            issue_titles = classified_titles
        
        # 각 이슈에 대해 상세 정보 수집
        print(f"\n2단계: 상세 정보 수집 (최대 {min(max_documents, len(issue_titles))}개)...")
        
        for idx, item in enumerate(issue_titles[:max_documents], 1):
            print(f"\n--- 처리 중: {idx}/{min(max_documents, len(issue_titles))} ---")
            print(f"제목: {item['title'][:50]}...")
            
            try:
                # 작성일시 추출
                print("  - 작성일시 추출 중...")
                post_datetime = workflow.get_post_datetime(item['link'])
                print(f"    작성일시: {post_datetime}")
                
                # 게시글 내용과 댓글 수집
                print("  - 게시글 내용 및 댓글 수집 중...")
                post_data = workflow.get_post_content_and_comments(item['link'], max_comments=20)
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
                    "page_num": item.get('page_num', 'unknown'),
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
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"문서 처리 실패: {e}")
                print(f"  ❌ 오류: {e}")
                continue
        
        # 결과 출력
        print(f"\n=== 문서 생성 완료 ===")
        print(f"생성된 문서 수: {len(documents)}")
        
        if documents:
            # JSON 파일로 저장
            filename = f"test_documents_hot_pages_{current_date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            print(f"\n문서가 {filename}에 저장되었습니다.")
            
            # 샘플 문서 출력
            print("\n=== 샘플 문서 ===")
            sample = documents[0]
            print(f"제목: {sample['title']}")
            print(f"링크: {sample['link']}")
            print(f"페이지: {sample['page_num']}")
            print(f"작성일시: {sample['post_datetime']}")
            print(f"댓글 수: {sample['comments_count']}")
            print(f"분석 길이: {len(sample['analysis'])} 문자")
            print(f"분석 미리보기: {sample['analysis'][:100]}...")
        
        return True, documents
        
    except Exception as e:
        logger.error(f"문서 생성 중 오류 발생: {e}")
        print(f"❌ 문서 생성 실패: {e}")
        return False, []

def main():
    """메인 함수"""
    print("Hot 게시판 2~10페이지 데이터 수집을 시작합니다...")
    print("이 스크립트는 테스트용 문서 생성을 위한 데이터를 수집합니다.\n")
    
    # 1단계: 데이터 수집
    success, titles_data = collect_hot_pages_data()
    
    if not success or not titles_data:
        print("\n💥 데이터 수집 실패!")
        return
    
    # 2단계: 테스트용 문서 생성 (선택사항)
    print(f"\n수집된 데이터로 테스트용 문서를 생성하시겠습니까? (y/n): ", end="")
    user_input = input().strip().lower()
    
    if user_input in ['y', 'yes', 'ㅇ']:
        doc_success, documents = create_test_documents(titles_data, max_documents=30)
        
        if doc_success:
            print("\n🎉 모든 작업 완료!")
        else:
            print("\n⚠️ 문서 생성은 실패했지만 데이터 수집은 완료되었습니다.")
    else:
        print("\n✅ 데이터 수집만 완료되었습니다.")

if __name__ == "__main__":
    main() 