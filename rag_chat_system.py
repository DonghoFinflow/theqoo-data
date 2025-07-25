#!/usr/bin/env python3
"""
RAG Chat System - JSON 파일을 Qdrant에 저장하고 대화하는 시스템
"""

import json
import os
import logging
from datetime import datetime
from qdrant_storage import QdrantStorage, load_documents_from_json
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGChatSystem:
    def __init__(self, collection_name="theqoo_documents"):
        """RAG 채팅 시스템 초기화"""
        self.storage = QdrantStorage(collection_name=collection_name)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        
    def load_and_store_json(self, json_filename):
        """JSON 파일을 로드하고 Qdrant에 저장"""
        print(f"📁 JSON 파일 로드 중: {json_filename}")
        
        if not os.path.exists(json_filename):
            print(f"❌ 파일이 존재하지 않습니다: {json_filename}")
            return False
        
        # JSON 파일에서 문서 로드
        documents = load_documents_from_json(json_filename)
        if not documents:
            print("❌ 문서를 로드할 수 없습니다.")
            return False
        
        print(f"✅ {len(documents)}개 문서 로드 완료")
        
        # Qdrant에 저장
        print("💾 Qdrant에 저장 중...")
        success = self.storage.store_documents(documents)
        
        if success:
            print("✅ Qdrant 저장 완료!")
            
            # 컬렉션 정보 출력
            info = self.storage.get_collection_info()
            if info:
                print(f"📊 컬렉션 벡터 수: {info.vectors_count}")
            
            return True
        else:
            print("❌ Qdrant 저장 실패!")
            return False
    
    def search_relevant_documents(self, query, limit=5):
        """쿼리와 관련된 문서 검색"""
        try:
            results = self.storage.search_similar_documents(query, limit=limit)
            return results
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}")
            return []
    
    def create_context_from_documents(self, search_results):
        """검색 결과로부터 컨텍스트 생성"""
        if not search_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            payload = result.payload
            context_parts.append(f"""
문서 {i} (유사도 점수: {result.score:.3f}):
제목: {payload['title']}
링크: {payload['link']}
작성일시: {payload.get('post_datetime', 'N/A')}
내용: {payload.get('content', '')[:300]}...
분석: {payload['analysis'][:500]}...
댓글 수: {payload.get('comments_count', 0)}개
---""")
        
        return "\n".join(context_parts)
    
    def generate_response_with_perplexity(self, query, context):
        """Perplexity API를 사용하여 응답 생성"""
        if not self.perplexity_api_key:
            return "Perplexity API 키가 설정되지 않았습니다."
        
        try:
            prompt = f"""
다음은 theqoo 게시판의 문서들입니다. 이 정보를 바탕으로 사용자의 질문에 답변해주세요.

=== 컨텍스트 ===
{context}

=== 사용자 질문 ===
{query}

위의 컨텍스트를 바탕으로 사용자의 질문에 친근하고 자연스럽게 답변해주세요. 
답변할 때는 관련된 문서의 정보를 언급하고, 필요하면 링크도 제공해주세요.
한국어로 답변해주세요.
"""

            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 theqoo 게시판의 정보를 바탕으로 질문에 답변하는 도우미입니다. 친근하고 자연스럽게 답변해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API 호출 실패: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Perplexity API 호출 실패: {e}")
            return f"응답 생성 중 오류가 발생했습니다: {e}"
    
    def chat(self, query, max_documents=5):
        """채팅 기능"""
        print(f"\n🔍 관련 문서 검색 중: '{query}'")
        
        # 관련 문서 검색
        search_results = self.search_relevant_documents(query, limit=max_documents)
        
        if not search_results:
            return "죄송합니다. 관련된 문서를 찾을 수 없습니다."
        
        print(f"✅ {len(search_results)}개 관련 문서 발견")
        
        # 컨텍스트 생성
        context = self.create_context_from_documents(search_results)
        
        # 응답 생성
        print("🤖 응답 생성 중...")
        response = self.generate_response_with_perplexity(query, context)
        
        return response
    
    def interactive_chat(self):
        """대화형 채팅 모드"""
        print("\n=== RAG Chat System ===")
        print("theqoo 게시판 데이터를 바탕으로 질문해주세요!")
        print("종료하려면 'quit', 'exit', '종료'를 입력하세요.\n")
        
        while True:
            try:
                user_input = input("질문: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                    print("채팅을 종료합니다. 안녕히 가세요!")
                    break
                
                if not user_input:
                    continue
                
                # 응답 생성
                response = self.chat(user_input)
                
                print(f"\n답변: {response}\n")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n채팅을 종료합니다. 안녕히 가세요!")
                break
            except Exception as e:
                logger.error(f"채팅 중 오류 발생: {e}")
                print(f"오류가 발생했습니다: {e}")

def main():
    """메인 함수"""
    print("RAG Chat System을 시작합니다...")
    
    # 사용 가능한 JSON 파일 찾기
    json_files = []
    for file in os.listdir('.'):
        if file.endswith('.json') and ('hot_pages' in file or 'test_documents' in file):
            json_files.append(file)
    
    if not json_files:
        print("❌ 사용 가능한 JSON 파일이 없습니다.")
        print("먼저 collect_hot_pages.py를 실행하여 데이터를 수집해주세요.")
        return
    
    print("\n📋 사용 가능한 JSON 파일:")
    for i, file in enumerate(json_files, 1):
        print(f"  {i}. {file}")
    
    # 파일 선택
    while True:
        try:
            choice = input(f"\n사용할 파일 번호를 선택하세요 (1-{len(json_files)}): ").strip()
            file_idx = int(choice) - 1
            
            if 0 <= file_idx < len(json_files):
                selected_file = json_files[file_idx]
                break
            else:
                print("올바른 번호를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
    
    # RAG 시스템 초기화
    rag_system = RAGChatSystem()
    
    # JSON 파일 로드 및 저장
    print(f"\n선택된 파일: {selected_file}")
    success = rag_system.load_and_store_json(selected_file)
    
    if not success:
        print("❌ 파일 로드 및 저장에 실패했습니다.")
        return
    
    # 대화형 채팅 시작
    rag_system.interactive_chat()

if __name__ == "__main__":
    main() 