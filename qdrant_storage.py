import json
import os
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import logging
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class QdrantStorage:
    def __init__(self, collection_name="theqoo_documents", host=None, port=6333):
        # 환경변수에서 Qdrant 설정 가져오기
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_key = os.getenv("QDRANT_KEY")
        
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
        
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # 컬렉션이 없으면 생성
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):
        """컬렉션이 없으면 생성"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"컬렉션 '{self.collection_name}' 생성됨")
            else:
                logger.info(f"컬렉션 '{self.collection_name}' 이미 존재함")
                
        except Exception as e:
            logger.error(f"컬렉션 생성/확인 실패: {e}")
    
    def _create_document_vector(self, document):
        """문서를 벡터로 변환"""
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
        
        # 벡터 생성
        vector = self.model.encode(text_for_vector).tolist()
        return vector
    
    def store_documents(self, documents):
        """문서들을 Qdrant에 저장"""
        if not documents:
            logger.warning("저장할 문서가 없습니다.")
            return False
        
        try:
            points = []
            
            for doc in documents:
                # 벡터 생성
                vector = self._create_document_vector(doc)
                
                # 메타데이터 준비
                payload = {
                    "title": doc['title'],
                    "link": doc['link'],
                    "post_datetime": doc.get('post_datetime', ''),
                    "content": doc.get('content', ''),
                    "comments": doc.get('comments', []),  # comments 필드 추가
                    "comments_count": doc.get('comments_count', 0),
                    "analysis": doc.get('analysis', ''),
                    "collected_date": doc.get('collected_date', ''),
                    "id": doc.get('id', f"doc_{hash(doc['title'])}"),
                    "text_for_search": f"{doc['title']} {doc.get('content', '')} {doc.get('analysis', '')}"
                }
                
                # Point 생성
                doc_id = doc.get('id', f"doc_{hash(doc['title'])}")
                point = PointStruct(
                    id=hash(doc_id) % (2**63),  # 64비트 정수로 변환
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            # 벡터 저장
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"{len(points)}개 문서를 Qdrant에 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"Qdrant 저장 실패: {e}")
            return False
    
    def search_similar_documents(self, query, limit=5):
        """유사한 문서 검색"""
        try:
            # 쿼리를 벡터로 변환
            query_vector = self.model.encode(query).tolist()
            
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
    current_date = datetime.now().strftime("%Y%m%d")
    json_filename = f"theqoo_documents_{current_date}.json"
    
    if not os.path.exists(json_filename):
        print(f"JSON 파일이 없습니다: {json_filename}")
        return
    
    # 문서 로드
    documents = load_documents_from_json(json_filename)
    if not documents:
        print("문서를 로드할 수 없습니다.")
        return
    
    # Qdrant에 저장
    storage = QdrantStorage()
    success = storage.store_documents(documents)
    
    if success:
        print("Qdrant 저장 완료!")
        
        # 컬렉션 정보 출력
        info = storage.get_collection_info()
        if info:
            print(f"컬렉션 벡터 수: {info.vectors_count}")
        
        # 검색 테스트
        print("\n=== 검색 테스트 ===")
        results = storage.search_similar_documents("최신 이슈", limit=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.payload['title']} (점수: {result.score:.3f})")
    else:
        print("Qdrant 저장 실패!")

if __name__ == "__main__":
    main() 