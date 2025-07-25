#!/usr/bin/env python3
"""
OpenAI Embedding을 사용하는 Qdrant Storage
"""

import json
import os
import logging
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIQdrantStorage:
    def __init__(self, collection_name="theqoo_documents_openai", host=None, port=6333):
        # 환경변수에서 Qdrant 설정 가져오기
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_key = os.getenv("QDRANT_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        # OpenAI 클라이언트 설정 (새로운 API)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # URL에서 호스트와 포트 추출
        if self.qdrant_url:
            if self.qdrant_url.startswith("http://"):
                host = self.qdrant_url[7:]  # "http://" 제거
            elif self.qdrant_url.startswith("https://"):
                host = self.qdrant_url[8:]  # "https://" 제거
            else:
                host = self.qdrant_url
            
            # 포트가 URL에 포함되어 있으면 추출
            if ":" in host:
                host, port_str = host.split(":", 1)
                port = int(port_str)
        else:
            host = host or "localhost"
        
        self.collection_name = collection_name
        self.host = host
        self.port = port
        
        # Qdrant 클라이언트 초기화
        if self.qdrant_key:
            self.client = QdrantClient(host=host, port=port, api_key=self.qdrant_key)
        else:
            self.client = QdrantClient(host=host, port=port)
        
        # 컬렉션이 없으면 생성 (text-embedding-3-small은 1536차원)
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):
        """컬렉션이 없으면 생성"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # text-embedding-3-small 차원
                )
                logger.info(f"컬렉션 '{self.collection_name}' 생성됨 (text-embedding-3-small)")
            else:
                logger.info(f"컬렉션 '{self.collection_name}' 이미 존재함")
                
        except Exception as e:
            logger.error(f"컬렉션 생성/확인 실패: {e}")
    
    def _create_document_vector_openai(self, document):
        """OpenAI 임베딩을 사용하여 문서를 벡터로 변환"""
        # 제목을 기본으로 사용
        text_for_vector = document['title']
        
        # 분석 내용이 있으면 추가
        if document.get('analysis'):
            text_for_vector += f" {document['analysis']}"
        
        # 내용이 있으면 추가
        if document.get('content'):
            content_text = document['content']
            if len(content_text) > 500:  # 너무 길면 잘라냄
                content_text = content_text[:500]
            text_for_vector += f" {content_text}"
        
        # 댓글도 일부 포함 (너무 길면 잘라냄)
        if document.get('comments'):
            comments_text = " ".join(document['comments'][:5])  # 상위 5개 댓글만
            if len(comments_text) > 500:  # 너무 길면 잘라냄
                comments_text = comments_text[:500]
            text_for_vector += f" {comments_text}"
        
        # 텍스트가 너무 짧으면 기본 텍스트 추가
        if len(text_for_vector.strip()) < 10:
            text_for_vector = f"theqoo 게시판: {text_for_vector}"
        
        logger.info(f"임베딩 생성 텍스트 길이: {len(text_for_vector)}자")
        logger.info(f"임베딩 생성 텍스트 미리보기: {text_for_vector[:100]}...")
        
        try:
            # OpenAI 임베딩 생성 (text-embedding-3-small 사용)
            response = self.openai_client.embeddings.create(
                input=text_for_vector,
                model="text-embedding-3-small"
            )
            vector = response.data[0].embedding
            
            # 벡터 검증
            if not vector or len(vector) != 1536:
                logger.error(f"벡터 생성 실패: 길이={len(vector) if vector else 0}, 예상=1536")
                raise ValueError("벡터 길이가 올바르지 않습니다")
            
            # 벡터가 모두 0인지 확인
            if all(v == 0.0 for v in vector):
                logger.error("생성된 벡터가 모두 0입니다")
                raise ValueError("벡터가 모두 0입니다")
            
            logger.info(f"벡터 생성 성공: 길이={len(vector)}, 첫 번째 값={vector[0]}")
            return vector
            
        except Exception as e:
            logger.error(f"OpenAI 임베딩 생성 실패: {e}")
            logger.error(f"실패한 텍스트: {text_for_vector[:200]}...")
            # 실패 시 None 반환 (0 벡터 대신)
            return None
    
    def store_documents(self, documents):
        """문서들을 Qdrant에 저장"""
        if not documents:
            logger.warning("저장할 문서가 없습니다.")
            return False
        
        logger.info(f"총 {len(documents)}개 문서 저장 시작")
        
        try:
            points = []
            success_count = 0
            error_count = 0
            
            for i, doc in enumerate(documents, 1):
                try:
                    logger.info(f"문서 {i}/{len(documents)} 처리 중: {doc.get('title', '제목 없음')[:50]}...")
                    
                    # OpenAI 임베딩으로 벡터 생성
                    vector = self._create_document_vector_openai(doc)
                    
                    # 벡터 생성 실패 확인
                    if vector is None:
                        logger.warning(f"문서 {i}의 벡터 생성 실패")
                        error_count += 1
                        continue
                    
                    # 벡터가 0으로만 채워져 있는지 확인
                    if all(v == 0.0 for v in vector):
                        logger.warning(f"문서 {i}의 벡터가 0으로만 채워져 있음 - 임베딩 생성 실패")
                        error_count += 1
                        continue
                    
                    # 메타데이터 준비
                    payload = {
                        "title": doc['title'],
                        "link": doc['link'],
                        "post_datetime": doc.get('post_datetime', ''),
                        "content": doc.get('content', ''),
                        "comments": doc.get('comments', []),
                        "comments_count": doc.get('comments_count', 0),
                        "analysis": doc.get('analysis', ''),
                        "collected_date": doc.get('collected_date', ''),
                        "id": doc.get('id', f"doc_{hash(doc['title'])}"),
                        "text_for_search": f"{doc['title']} {doc.get('content', '')} {doc.get('analysis', '')}",
                        "embedding_model": "text-embedding-3-small"
                    }
                    
                    # 벡터 최종 검증
                    if len(vector) != 1536:
                        logger.error(f"문서 {i}의 벡터 길이가 잘못됨: {len(vector)} (예상: 1536)")
                        error_count += 1
                        continue
                    
                    # Point 생성
                    doc_id = doc.get('id', f"doc_{hash(doc['title'])}")
                    point = PointStruct(
                        id=hash(doc_id) % (2**63),  # 64비트 정수로 변환
                        vector=vector,
                        payload=payload
                    )
                    points.append(point)
                    success_count += 1
                    logger.info(f"문서 {i} 포인트 생성 완료: 벡터 길이={len(vector)}")
                    
                except Exception as doc_error:
                    logger.error(f"문서 {i} 처리 실패: {doc_error}")
                    error_count += 1
                    continue
            
            logger.info(f"벡터 생성 완료: 성공 {success_count}개, 실패 {error_count}개")
            
            if not points:
                logger.error("저장할 포인트가 없습니다.")
                return False
            
            # 벡터 저장
            logger.info(f"Qdrant에 {len(points)}개 포인트 저장 중...")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"{len(points)}개 문서를 text-embedding-3-small으로 Qdrant에 저장 완료")
            
            # 저장 후 검증
            logger.info("저장 후 벡터 검증 중...")
            try:
                # 몇 개의 포인트를 조회해서 벡터가 제대로 저장되었는지 확인
                test_points = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=3,
                    with_payload=False,
                    with_vectors=True
                )
                
                if test_points and len(test_points[0]) > 0:
                    for i, point in enumerate(test_points[0]):
                        if point.vector is None:
                            logger.error(f"저장된 포인트 {i}의 벡터가 None입니다!")
                        else:
                            logger.info(f"저장된 포인트 {i}의 벡터 길이: {len(point.vector)}")
                else:
                    logger.warning("저장 후 포인트 조회 실패")
                    
            except Exception as verify_error:
                logger.error(f"저장 후 검증 실패: {verify_error}")
            
            return True
            
        except Exception as e:
            logger.error(f"Qdrant 저장 실패: {e}")
            return False
    
    def search_similar_documents(self, query, limit=5):
        """OpenAI 임베딩을 사용하여 유사한 문서 검색"""
        try:
            # 쿼리를 OpenAI 임베딩으로 변환
            response = self.openai_client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_vector = response.data[0].embedding
            
            # 유사도 검색
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            return search_result
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def get_collection_info(self):
        """컬렉션 정보 조회"""
        try:
            info = self.client.get_collection(self.collection_name)
            return info
        except Exception as e:
            logger.error(f"컬렉션 정보 조회 실패: {e}")
            return None

def load_documents_from_json(filename):
    """JSON 파일에서 문서 로드"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        logger.info(f"JSON 파일에서 {len(documents)}개 문서 로드됨: {filename}")
        return documents
    except Exception as e:
        logger.error(f"JSON 파일 로드 실패: {e}")
        return []

def main():
    """테스트용 메인 함수"""
    # JSON 파일에서 문서 로드
    json_filename = "test_documents_hot_pages_2025-07-21.json"
    
    if not os.path.exists(json_filename):
        print(f"JSON 파일이 없습니다: {json_filename}")
        return
    
    # 문서 로드
    documents = load_documents_from_json(json_filename)
    if not documents:
        print("문서를 로드할 수 없습니다.")
        return
    
    # OpenAI Qdrant에 저장
    storage = OpenAIQdrantStorage()
    success = storage.store_documents(documents)
    
    if success:
        print("OpenAI Qdrant 저장 완료!")
        
        # 컬렉션 정보 출력
        info = storage.get_collection_info()
        if info:
            print(f"컬렉션 벡터 수: {info.vectors_count}")
        
        # 검색 테스트
        print("\n=== text-embedding-3-small 검색 테스트 ===")
        results = storage.search_similar_documents("AI 기술", limit=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.payload['title']} (점수: {result.score:.3f})")
    else:
        print("text-embedding-3-small Qdrant 저장 실패!")

if __name__ == "__main__":
    main() 