#!/usr/bin/env python3
"""
Qdrant 컬렉션 상태 확인 스크립트
"""

import os
import logging
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

def check_collection_status(collection_name="theqoo_documents_openai"):
    """컬렉션 상태를 자세히 확인"""
    
    # Qdrant 설정
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_KEY")
    
    # URL에서 호스트와 포트 추출
    if qdrant_url:
        if qdrant_url.startswith("http://"):
            host = qdrant_url[7:]  # "http://" 제거
        elif qdrant_url.startswith("https://"):
            host = qdrant_url[8:]  # "https://" 제거
        else:
            host = qdrant_url
        
        # 포트가 URL에 포함되어 있으면 추출
        if ":" in host:
            host, port_str = host.split(":", 1)
            port = int(port_str)
        else:
            port = 6333
    else:
        host = "localhost"
        port = 6333
    
    # Qdrant 클라이언트 초기화
    if qdrant_key:
        client = QdrantClient(host=host, port=port, api_key=qdrant_key)
    else:
        client = QdrantClient(host=host, port=port)
    
    try:
        print(f"=== 컬렉션 '{collection_name}' 상태 확인 ===")
        
        # 모든 컬렉션 목록 확인
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        print(f"전체 컬렉션 목록: {collection_names}")
        
        if collection_name in collection_names:
            print(f"✅ 컬렉션 '{collection_name}' 존재함")
            
            # 컬렉션 상세 정보 확인
            info = client.get_collection(collection_name)
            print(f"컬렉션 정보:")
            print(f"  - 벡터 수: {info.vectors_count}")
            print(f"  - 포인트 수: {info.points_count}")
            print(f"  - 세그먼트 수: {info.segments_count}")
            print(f"  - 설정: {info.config}")
            
            # 실제 포인트 수 확인
            try:
                points = client.scroll(
                    collection_name=collection_name,
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                print(f"  - 실제 포인트 수: {len(points[0])}")
                
                if len(points[0]) > 0:
                    print("✅ 컬렉션에 데이터가 있습니다!")
                    return True, info.vectors_count
                else:
                    print("❌ 컬렉션에 데이터가 없습니다.")
                    return False, 0
                    
            except Exception as e:
                print(f"포인트 조회 실패: {e}")
                return False, 0
        else:
            print(f"❌ 컬렉션 '{collection_name}'이 존재하지 않습니다.")
            return False, 0
            
    except Exception as e:
        logger.error(f"컬렉션 상태 확인 실패: {e}")
        return False, 0

def main():
    """메인 함수"""
    print("=== Qdrant 컬렉션 상태 확인 ===")
    
    # 기본 컬렉션명
    collection_name = "theqoo_documents_openai"
    
    # 사용자 입력 받기
    user_input = input(f"확인할 컬렉션명을 입력하세요 (기본값: {collection_name}): ").strip()
    if user_input:
        collection_name = user_input
    
    # 상태 확인
    has_data, vector_count = check_collection_status(collection_name)
    
    if has_data:
        print(f"\n✅ 컬렉션 '{collection_name}'에 {vector_count}개의 벡터가 있습니다.")
        print("Streamlit 앱에서 '기존 데이터로 검색 시작' 버튼을 클릭하면 검색할 수 있습니다.")
    else:
        print(f"\n❌ 컬렉션 '{collection_name}'에 데이터가 없습니다.")
        print("먼저 JSON 파일을 로드하여 데이터를 저장해주세요.")

if __name__ == "__main__":
    main() 