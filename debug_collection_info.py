#!/usr/bin/env python3
"""
Qdrant 컬렉션 정보 디버깅 스크립트
"""

import os
import logging
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

def debug_collection_info(collection_name="theqoo_documents_openai"):
    """컬렉션 정보를 자세히 디버깅"""
    
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
        print(f"=== 컬렉션 '{collection_name}' 정보 디버깅 ===")
        
        # 컬렉션 정보 가져오기
        info = client.get_collection(collection_name)
        print(f"컬렉션 정보 타입: {type(info)}")
        print(f"컬렉션 정보: {info}")
        
        # 모든 속성 확인
        print("\n=== 모든 속성 확인 ===")
        for attr in dir(info):
            if not attr.startswith('_'):
                try:
                    value = getattr(info, attr)
                    print(f"{attr}: {value} (타입: {type(value)})")
                except Exception as e:
                    print(f"{attr}: 에러 - {e}")
        
        # 특정 속성들 확인
        print("\n=== 주요 속성 확인 ===")
        attributes_to_check = [
            'vectors_count', 'points_count', 'segments_count', 
            'config', 'status', 'optimizer_status', 'payload_indexing_status'
        ]
        
        for attr in attributes_to_check:
            if hasattr(info, attr):
                value = getattr(info, attr)
                print(f"{attr}: {value}")
            else:
                print(f"{attr}: 속성이 없음")
        
        # 실제 포인트 수 확인
        print("\n=== 실제 포인트 확인 ===")
        try:
            points = client.scroll(
                collection_name=collection_name,
                limit=10,
                with_payload=False,
                with_vectors=False
            )
            print(f"Scroll 결과: {points}")
            print(f"실제 포인트 수: {len(points[0]) if points and len(points) > 0 else 0}")
        except Exception as e:
            print(f"Scroll 실패: {e}")
            
    except Exception as e:
        logger.error(f"컬렉션 정보 디버깅 실패: {e}")

def main():
    """메인 함수"""
    print("=== Qdrant 컬렉션 정보 디버깅 ===")
    
    # 기본 컬렉션명
    collection_name = "theqoo_documents_openai"
    
    # 사용자 입력 받기
    user_input = input(f"확인할 컬렉션명을 입력하세요 (기본값: {collection_name}): ").strip()
    if user_input:
        collection_name = user_input
    
    # 디버깅 실행
    debug_collection_info(collection_name)

if __name__ == "__main__":
    main() 