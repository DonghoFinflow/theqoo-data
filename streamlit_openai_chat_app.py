#!/usr/bin/env python3
"""
Streamlit OpenAI RAG Chat Application
text-embedding-3-small을 사용하여 JSON 파일을 Qdrant에 저장하고 Streamlit으로 채팅하는 웹 애플리케이션
"""

import streamlit as st
import json
import os
import logging
from datetime import datetime
from openai_qdrant_storage import OpenAIQdrantStorage, load_documents_from_json
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitOpenAIRAGChat:
    def __init__(self, collection_name="theqoo_documents_openai"):
        """Streamlit OpenAI RAG 채팅 시스템 초기화"""
        self.collection_name = collection_name
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        
        # OpenAI API 키 확인
        if not os.getenv('OPENAI_API_KEY'):
            st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            self.storage = None
            return
        
        # OpenAI Qdrant 스토리지 초기화
        try:
            self.storage = OpenAIQdrantStorage(collection_name=collection_name)
            st.success("✅ OpenAI Qdrant 연결 성공! (text-embedding-3-small)")
        except Exception as e:
            st.error(f"❌ OpenAI Qdrant 연결 실패: {e}")
            self.storage = None
    
    def load_and_store_json(self, json_filename):
        """JSON 파일을 로드하고 OpenAI Qdrant에 저장"""
        if not os.path.exists(json_filename):
            st.error(f"❌ 파일이 존재하지 않습니다: {json_filename}")
            return False
        
        try:
            # JSON 파일에서 문서 로드
            documents = load_documents_from_json(json_filename)
            if not documents:
                st.error("❌ 문서를 로드할 수 없습니다.")
                return False
            
            st.success(f"✅ {len(documents)}개 문서 로드 완료")
            
            # OpenAI Qdrant에 저장
            with st.spinner("💾 OpenAI Qdrant에 저장 중..."):
                success = self.storage.store_documents(documents)
            
            if success:
                st.success("✅ OpenAI Qdrant 저장 완료!")
                
                # 컬렉션 정보 출력
                info = self.storage.get_collection_info()
                if info:
                    st.info(f"📊 컬렉션 벡터 수: {info.vectors_count}")
                
                return True
            else:
                st.error("❌ OpenAI Qdrant 저장 실패!")
                return False
                
        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류: {e}")
            return False
    
    def search_relevant_documents(self, query, limit=5):
        """쿼리와 관련된 문서 검색"""
        if not self.storage:
            return []
        
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
            content_preview = payload.get('content', '')[:300] if payload.get('content') else '내용 없음'
            analysis_preview = payload.get('analysis', '')[:500] if payload.get('analysis') else '분석 없음'
            
            context_parts.append(f"""
문서 {i} (유사도 점수: {result.score:.3f}):
제목: {payload['title']}
링크: {payload['link']}
작성일시: {payload.get('post_datetime', 'N/A')}
내용: {content_preview}...
분석: {analysis_preview}...
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
        if not self.storage:
            return "OpenAI Qdrant 연결이 설정되지 않았습니다.", []
        
        # 관련 문서 검색
        search_results = self.search_relevant_documents(query, limit=max_documents)
        
        if not search_results:
            return "죄송합니다. 관련된 문서를 찾을 수 없습니다.", []
        
        # 컨텍스트 생성
        context = self.create_context_from_documents(search_results)
        
        # 응답 생성
        response = self.generate_response_with_perplexity(query, context)
        
        return response, search_results
    
    def check_collection_has_data(self):
        """컬렉션에 데이터가 있는지 안전하게 확인"""
        if not self.storage:
            return False, 0
        
        try:
            # 컬렉션 정보 확인
            info = self.storage.get_collection_info()
            if not info:
                logger.error("컬렉션 정보를 가져올 수 없습니다.")
                return False, 0
            
            # points_count 확인 (vectors_count가 None이어도 points_count로 판단)
            if hasattr(info, 'points_count') and info.points_count is not None and info.points_count > 0:
                logger.info(f"컬렉션에 {info.points_count}개의 포인트가 있습니다.")
                return True, info.points_count
            
            # vectors_count 확인 (백업)
            if hasattr(info, 'vectors_count') and info.vectors_count is not None and info.vectors_count > 0:
                logger.info(f"vectors_count로 판단: {info.vectors_count}개")
                return True, info.vectors_count
            
            # 실제 데이터가 있는지 확인 (scroll로 실제 포인트 조회)
            try:
                points = self.storage.client.scroll(
                    collection_name=self.collection_name,
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                actual_points = len(points[0]) if points and len(points) > 0 else 0
                
                if actual_points > 0:
                    logger.info(f"컬렉션에 {actual_points}개의 실제 포인트가 있습니다.")
                    return True, actual_points
                else:
                    logger.warning("컬렉션에 실제 포인트가 없습니다.")
                    return False, 0
                    
            except Exception as scroll_error:
                logger.error(f"포인트 조회 실패: {scroll_error}")
                return False, 0
                    
        except Exception as e:
            logger.error(f"컬렉션 데이터 확인 실패: {e}")
            return False, 0

def main():
    """Streamlit 메인 앱"""
    st.set_page_config(
        page_title="OpenAI RAG Chat System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 OpenAI RAG Chat System")
    st.markdown("text-embedding-3-small을 사용한 theqoo 게시판 데이터 기반 채팅 시스템")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 컬렉션 선택
        collection_name = st.selectbox(
            "컬렉션 선택",
            ["theqoo_documents_openai", "theqoo_documents_openai_v2"],
            index=0
        )
        
        # JSON 파일 선택
        json_files = []
        for file in os.listdir('.'):
            if file.endswith('.json') and ('hot_pages' in file or 'test_documents' in file):
                json_files.append(file)
        
        if json_files:
            selected_file = st.selectbox(
                "JSON 파일 선택",
                json_files,
                index=0 if 'test_documents_hot_pages_2025-07-21.json' in json_files else 0
            )
            
            if st.button("📁 OpenAI Qdrant에 데이터 로드"):
                rag_system = StreamlitOpenAIRAGChat(collection_name=collection_name)
                success = rag_system.load_and_store_json(selected_file)
                
                if success:
                    st.session_state.rag_system = rag_system
                    st.session_state.data_loaded = True
            
            # 기존 데이터가 있는지 확인하고 바로 검색 가능하도록 설정
            if st.button("🔍 기존 데이터로 검색 시작"):
                st.info(f"🔍 컬렉션 '{collection_name}'에서 데이터 확인 중...")
                rag_system = StreamlitOpenAIRAGChat(collection_name=collection_name)
                if rag_system.storage:
                    # 안전한 컬렉션 데이터 확인
                    has_data, vector_count = rag_system.check_collection_has_data()
                    if has_data:
                        st.session_state.rag_system = rag_system
                        st.session_state.data_loaded = True
                        st.success(f"✅ 기존 데이터로 검색 준비 완료! (벡터 수: {vector_count}개)")
                    else:
                        st.error(f"❌ 컬렉션 '{collection_name}'에 데이터가 없습니다. 먼저 데이터를 로드해주세요.")
                else:
                    st.error("❌ OpenAI Qdrant 연결에 실패했습니다.")
        else:
            st.warning("사용 가능한 JSON 파일이 없습니다.")
        
        # 검색 설정
        st.header("🔍 검색 설정")
        max_documents = st.slider("최대 검색 문서 수", 1, 10, 5)
        
        # API 키 상태 확인
        st.header("🔑 API 상태")
        if os.getenv('OPENAI_API_KEY'):
            st.success("✅ OpenAI API 키 설정됨")
        else:
            st.error("❌ OpenAI API 키가 설정되지 않음")
            
        if os.getenv('PERPLEXITY_API_KEY'):
            st.success("✅ Perplexity API 키 설정됨")
        else:
            st.error("❌ Perplexity API 키가 설정되지 않음")
    
    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    # 환영 메시지
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "안녕하세요! text-embedding-3-small을 사용한 RAG 채팅 시스템입니다. 먼저 사이드바에서 '기존 데이터로 검색 시작' 버튼을 클릭하거나 JSON 파일을 로드해주세요."
        })
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요...", key="chat_input"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 데이터가 로드되지 않았으면 안내
        if not st.session_state.data_loaded or st.session_state.rag_system is None:
            with st.chat_message("assistant"):
                st.error("먼저 사이드바에서 '기존 데이터로 검색 시작' 버튼을 클릭하거나 JSON 파일을 로드해주세요.")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "먼저 사이드바에서 '기존 데이터로 검색 시작' 버튼을 클릭하거나 JSON 파일을 로드해주세요."
            })
        else:
            # 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("🤖 text-embedding-3-small으로 응답 생성 중..."):
                    response, search_results = st.session_state.rag_system.chat(prompt, max_documents)
                    st.markdown(response)
                
                # 검색 결과 표시 (접을 수 있는 섹션)
                if search_results:
                    with st.expander(f"🔍 관련 문서 ({len(search_results)}개) - text-embedding-3-small"):
                        for i, result in enumerate(search_results, 1):
                            payload = result.payload
                            st.markdown(f"""
                            **문서 {i}** (유사도: {result.score:.3f})
                            - **제목**: {payload['title']}
                            - **링크**: {payload['link']}
                            - **작성일시**: {payload.get('post_datetime', 'N/A')}
                            - **댓글 수**: {payload.get('comments_count', 0)}개
                            - **임베딩 모델**: {payload.get('embedding_model', 'text-embedding-3-small')}
                            """)
                            if payload.get('content'):
                                st.markdown(f"**내용 미리보기**: {payload.get('content', '')[:200]}...")
                            if payload.get('analysis'):
                                st.markdown(f"**분석**: {payload['analysis'][:300]}...")
                            if payload.get('comments'):
                                comments_preview = ", ".join(payload['comments'][:3])
                                if len(comments_preview) > 200:
                                    comments_preview = comments_preview[:200] + "..."
                                st.markdown(f"**댓글 미리보기**: {comments_preview}")
                            st.divider()
            
            # 어시스턴트 메시지 추가
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 채팅 히스토리 초기화 버튼
    if st.session_state.messages:
        if st.button("🗑️ 채팅 히스토리 초기화"):
            st.session_state.messages = []
            st.session_state.data_loaded = False
            st.session_state.rag_system = None
            st.rerun()

if __name__ == "__main__":
    main() 