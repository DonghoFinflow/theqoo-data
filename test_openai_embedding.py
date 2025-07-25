#!/usr/bin/env python3
"""
OpenAI 임베딩 테스트 스크립트
"""

import os
from openai_qdrant_storage import OpenAIQdrantStorage, load_documents_from_json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_openai_embedding():
    """OpenAI 임베딩 테스트"""
    
    # OpenAI API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return False
    
    print("✅ OpenAI API 키 확인됨")
    
    # JSON 파일 로드
    filename = "test_documents_hot_pages_2025-07-21.json"
    print(f"📁 JSON 파일 로드 중: {filename}")
    
    documents = load_documents_from_json(filename)
    if not documents:
        print("❌ 문서를 로드할 수 없습니다.")
        return False
    
    print(f"✅ {len(documents)}개 문서 로드 완료")
    
    # OpenAI Qdrant 스토리지 초기화
    print("🔧 OpenAI Qdrant 스토리지 초기화...")
    storage = OpenAIQdrantStorage(collection_name="test_openai_collection")
    
    # 처음 3개 문서만 테스트
    test_documents = documents[:3]
    print(f"📝 {len(test_documents)}개 문서로 테스트 시작...")
    
    # 저장 테스트
    success = storage.store_documents(test_documents)
    
    if success:
        print("✅ OpenAI 임베딩 저장 성공!")
        
        # 컬렉션 정보 확인
        info = storage.get_collection_info()
        if info:
            print(f"📊 컬렉션 벡터 수: {info.vectors_count}")
        
        # 검색 테스트
        print("\n🔍 검색 테스트...")
        test_queries = [
            "AI 기술",
            "게임 업계",
            "환경 보호",
            "디지털 헬스케어"
        ]
        
        for query in test_queries:
            print(f"\n검색어: '{query}'")
            results = storage.search_similar_documents(query, limit=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result.payload['title']} (점수: {result.score:.3f})")
            else:
                print("  검색 결과 없음")
        
        return True
    else:
        print("❌ 저장 실패!")
        return False

def main():
    """메인 함수"""
    print("OpenAI 임베딩 테스트를 시작합니다...")
    
    success = test_openai_embedding()
    
    if success:
        print("\n🎉 OpenAI 임베딩 테스트 성공!")
        print("\n이제 다음 명령어로 OpenAI RAG 채팅을 테스트할 수 있습니다:")
        print("streamlit run streamlit_openai_chat_app.py")
    else:
        print("\n💥 OpenAI 임베딩 테스트 실패!")

if __name__ == "__main__":
    main() 