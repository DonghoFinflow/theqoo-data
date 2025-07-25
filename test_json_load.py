#!/usr/bin/env python3
"""
JSON 파일 로드 테스트 스크립트
"""

import json
from qdrant_storage import QdrantStorage, load_documents_from_json

def test_json_load():
    """JSON 파일 로드 테스트"""
    
    # JSON 파일 로드
    filename = "hot_pages_2_10_2025-07-21.json"
    print(f"📁 JSON 파일 로드 중: {filename}")
    
    documents = load_documents_from_json(filename)
    if not documents:
        print("❌ 문서를 로드할 수 없습니다.")
        return False
    
    print(f"✅ {len(documents)}개 문서 로드 완료")
    
    # 첫 번째 문서 구조 확인
    if documents:
        first_doc = documents[0]
        print(f"\n📋 첫 번째 문서 구조:")
        for key, value in first_doc.items():
            print(f"  {key}: {type(value).__name__} = {str(value)[:100]}...")
    
    # Qdrant에 저장 테스트
    print(f"\n💾 Qdrant에 저장 테스트...")
    storage = QdrantStorage()
    
    # 처음 5개 문서만 테스트
    test_documents = documents[:5]
    success = storage.store_documents(test_documents)
    
    if success:
        print(f"✅ {len(test_documents)}개 문서 저장 성공!")
        
        # 컬렉션 정보 확인
        info = storage.get_collection_info()
        if info:
            print(f"📊 컬렉션 벡터 수: {info.vectors_count}")
        
        # 검색 테스트
        print(f"\n🔍 검색 테스트...")
        results = storage.search_similar_documents("AI 기술", limit=3)
        print(f"✅ {len(results)}개 검색 결과")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.payload['title']} (점수: {result.score:.3f})")
        
        return True
    else:
        print("❌ 저장 실패!")
        return False

if __name__ == "__main__":
    test_json_load() 