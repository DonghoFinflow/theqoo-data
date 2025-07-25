#!/usr/bin/env python3
"""
Qdrant 컬렉션 삭제 및 재생성 스크립트
"""

import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

def delete_and_recreate_collection(collection_name="theqoo_documents_openai"):
    """컬렉션을 삭제하고 다시 생성"""
    
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
        # 기존 컬렉션 확인
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name in collection_names:
            print(f"컬렉션 '{collection_name}' 삭제 중...")
            client.delete_collection(collection_name=collection_name)
            print(f"컬렉션 '{collection_name}' 삭제 완료")
        else:
            print(f"컬렉션 '{collection_name}'이 존재하지 않습니다.")
        
        # 새 컬렉션 생성
        print(f"새 컬렉션 '{collection_name}' 생성 중...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # text-embedding-3-small 차원
        )
        print(f"컬렉션 '{collection_name}' 생성 완료 (text-embedding-3-small)")
        
        # 컬렉션 정보 확인
        info = client.get_collection(collection_name)
        print(f"컬렉션 벡터 수: {info.vectors_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"컬렉션 삭제/생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("=== Qdrant 컬렉션 삭제 및 재생성 ===")
    
    # 기본 컬렉션명
    collection_name = "theqoo_documents_openai"
    
    # 사용자 입력 받기
    user_input = input(f"컬렉션명을 입력하세요 (기본값: {collection_name}): ").strip()
    if user_input:
        collection_name = user_input
    
    # 확인
    confirm = input(f"컬렉션 '{collection_name}'을 삭제하고 다시 생성하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("취소되었습니다.")
        return
    
    # 삭제 및 재생성
    success = delete_and_recreate_collection(collection_name)
    
    if success:
        print("\n✅ 컬렉션 삭제 및 재생성 완료!")
        print("이제 새로운 text-embedding-3-small 모델로 데이터를 저장할 수 있습니다.")
    else:
        print("\n❌ 컬렉션 삭제 및 재생성 실패!")

if __name__ == "__main__":
    main() 