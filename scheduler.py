import schedule
import time
import logging
from datetime import datetime
import os
from main_workflow import TheqooWorkflow
from qdrant_storage import QdrantStorage, load_documents_from_json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('theqoo_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TheqooScheduler:
    def __init__(self):
        self.workflow = TheqooWorkflow()
        self.storage = QdrantStorage()
        
    def daily_job(self):
        """하루에 한 번 실행되는 작업"""
        logger.info("=== 일일 Theqoo 데이터 수집 작업 시작 ===")
        
        try:
            # 1. 워크플로우 실행
            logger.info("1단계: 워크플로우 실행")
            documents = self.workflow.run_workflow(page_num=2, start_idx=5, end_idx=15)
            
            if not documents:
                logger.error("문서 생성 실패")
                return False
            
            # 2. JSON 파일로 저장
            logger.info("2단계: JSON 파일 저장")
            saved_file = self.workflow.save_documents(documents)
            
            if not saved_file:
                logger.error("JSON 파일 저장 실패")
                return False
            
            # 3. Qdrant에 저장
            logger.info("3단계: Qdrant 벡터 스토어 저장")
            success = self.storage.store_documents(documents)
            
            if success:
                logger.info(f"=== 작업 완료: {len(documents)}개 문서 처리됨 ===")
                
                # 컬렉션 정보 출력
                info = self.storage.get_collection_info()
                if info:
                    logger.info(f"Qdrant 컬렉션 벡터 수: {info.vectors_count}")
                
                return True
            else:
                logger.error("Qdrant 저장 실패")
                return False
                
        except Exception as e:
            logger.error(f"일일 작업 실행 중 오류: {e}")
            return False
    
    def test_job(self):
        """테스트용 작업 (적은 수의 문서로 빠른 테스트)"""
        logger.info("=== 테스트 작업 시작 ===")
        
        try:
            # 적은 수의 문서로 테스트
            documents = self.workflow.run_workflow(page_num=2, start_idx=5, end_idx=8)
            
            if documents:
                saved_file = self.workflow.save_documents(documents, "test_documents.json")
                success = self.storage.store_documents(documents)
                
                if success:
                    logger.info(f"테스트 완료: {len(documents)}개 문서")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"테스트 작업 오류: {e}")
            return False
    
    def run_scheduler(self, test_mode=False):
        """스케줄러 실행"""
        if test_mode:
            logger.info("테스트 모드로 실행")
            self.test_job()
            return
        
        # 매일 오전 9시에 실행
        schedule.every().day.at("09:00").do(self.daily_job)
        
        # 또는 매일 자정에 실행하려면:
        # schedule.every().day.at("00:00").do(self.daily_job)
        
        logger.info("스케줄러 시작됨 - 매일 오전 9시에 실행됩니다.")
        logger.info("프로그램을 종료하려면 Ctrl+C를 누르세요.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("스케줄러 종료됨")

def manual_run():
    """수동 실행 함수"""
    scheduler = TheqooScheduler()
    success = scheduler.daily_job()
    
    if success:
        print("수동 실행 완료!")
    else:
        print("수동 실행 실패!")

def check_qdrant_status():
    """Qdrant 상태 확인"""
    try:
        storage = QdrantStorage()
        info = storage.get_collection_info()
        
        if info:
            print(f"Qdrant 컬렉션 정보:")
            print(f"- 이름: {info.name}")
            print(f"- 벡터 수: {info.vectors_count}")
            print(f"- 상태: {info.status}")
        else:
            print("Qdrant 연결 실패")
            
    except Exception as e:
        print(f"Qdrant 상태 확인 실패: {e}")

def search_documents(query, limit=5):
    """문서 검색"""
    try:
        storage = QdrantStorage()
        results = storage.search_similar_documents(query, limit)
        
        print(f"\n'{query}' 검색 결과:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.payload['title']}")
            print(f"   점수: {result.score:.3f}")
            print(f"   날짜: {result.payload['collected_date']}")
            print()
            
    except Exception as e:
        print(f"검색 실패: {e}")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Theqoo 데이터 수집 스케줄러')
    parser.add_argument('--mode', choices=['scheduler', 'manual', 'test', 'status', 'search'], 
                       default='manual', help='실행 모드')
    parser.add_argument('--query', type=str, help='검색 쿼리 (search 모드에서 사용)')
    parser.add_argument('--limit', type=int, default=5, help='검색 결과 수 (search 모드에서 사용)')
    
    args = parser.parse_args()
    
    if args.mode == 'scheduler':
        scheduler = TheqooScheduler()
        scheduler.run_scheduler()
    elif args.mode == 'manual':
        manual_run()
    elif args.mode == 'test':
        scheduler = TheqooScheduler()
        scheduler.run_scheduler(test_mode=True)
    elif args.mode == 'status':
        check_qdrant_status()
    elif args.mode == 'search':
        if not args.query:
            print("검색 쿼리를 입력해주세요: --query '검색어'")
            return
        search_documents(args.query, args.limit)

if __name__ == "__main__":
    main() 