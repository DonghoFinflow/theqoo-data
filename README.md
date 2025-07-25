# Theqoo 데이터 수집 및 분석 시스템

이 프로젝트는 Theqoo 게시판에서 핫타이틀을 수집하고, 정치가 아닌 이슈들을 분류하여 댓글을 수집한 후, Perplexity API로 분석하여 Qdrant 벡터 스토어에 저장하는 시스템입니다.

## 🚀 주요 기능

1. **핫타이틀 수집**: Theqoo 게시판에서 인기 게시글 제목 수집
2. **자동 분류**: Perplexity API를 사용하여 정치 관련 여부 자동 분류
3. **댓글 수집**: 정치가 아닌 이슈들의 댓글 수집
4. **AI 분석**: Perplexity API로 관련 기사와 이벤트 분석
5. **벡터 저장**: Qdrant 벡터 스토어에 저장하여 RAG 시스템 구축
6. **자동 스케줄링**: 하루에 한 번 자동 실행

## 📋 요구사항

- Python 3.8+
- Chrome 브라우저
- Qdrant 서버 (Docker 또는 로컬 설치)

## 🛠️ 설치 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Qdrant 서버 실행

Docker를 사용하는 경우:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

또는 로컬 설치:
```bash
# Qdrant 공식 문서 참조
```

### 3. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Perplexity API 키
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Qdrant 설정
QDRANT_URL=http://localhost:6333
QDRANT_KEY=your_qdrant_api_key_here
```

참고: `env_example.txt` 파일을 `.env`로 복사하여 사용할 수 있습니다.

## 📁 파일 구조

```
PythonProject/
├── main_workflow.py          # 메인 워크플로우 실행
├── qdrant_storage.py         # Qdrant 벡터 스토어 관리
├── scheduler.py              # 스케줄러 및 실행 관리
├── requirements.txt          # 의존성 패키지
├── README.md                 # 프로젝트 설명서
├── env_example.txt           # 환경변수 예시 파일
├── .env                      # 환경변수 설정 파일 (사용자가 생성)
├── theqoo_hotTitle.py        # 핫타이틀 수집 (기존)
├── classify_title.py         # 제목 분류 (기존)
├── theqoo_comment.py         # 댓글 수집 (기존)
├── perplexity.py             # Perplexity 분석 (기존)
└── get_date.py               # 날짜 추출 (기존)
```

## 🚀 사용 방법

### 1. 수동 실행

```bash
# 전체 워크플로우 실행
python scheduler.py --mode manual

# 테스트 실행 (적은 수의 문서)
python scheduler.py --mode test
```

### 2. 스케줄러 실행

```bash
# 매일 오전 9시에 자동 실행
python scheduler.py --mode scheduler
```

### 3. Qdrant 상태 확인

```bash
# Qdrant 컬렉션 정보 확인
python scheduler.py --mode status
```

### 4. 문서 검색

```bash
# 저장된 문서 검색
python scheduler.py --mode search --query "검색어" --limit 5
```

## 📊 생성되는 데이터 구조

각 문서는 다음과 같은 구조로 저장됩니다:

```json
{
  "id": "theqoo_20241201_1",
  "title": "게시글 제목",
  "link": "https://theqoo.net/hot/...",
  "post_datetime": "2024-12-01 10:30:00",
  "content": "게시글 본문 내용",
  "comments": ["댓글1", "댓글2", ...],
  "comments_count": 15,
  "analysis": "Perplexity API 분석 결과",
  "collected_date": "2024-12-01"
}
```

## 🔧 설정 옵션

### 워크플로우 설정 (`main_workflow.py`)

```python
# 페이지 번호 및 수집 범위 조정
documents = workflow.run_workflow(
    page_num=2,      # 수집할 페이지 번호
    start_idx=5,     # 시작 인덱스
    end_idx=15       # 종료 인덱스
)
```

### Qdrant 설정

환경변수를 통해 Qdrant 설정을 관리합니다:

```bash
# .env 파일에서 설정
QDRANT_URL=http://localhost:6333
QDRANT_KEY=your_qdrant_api_key_here
```

또는 코드에서 직접 설정:

```python
storage = QdrantStorage(
    collection_name="theqoo_documents",  # 컬렉션 이름
    host="localhost",                    # 서버 호스트 (기본값)
    port=6333                           # 서버 포트 (기본값)
)
```

### 스케줄러 설정 (`scheduler.py`)

```python
# 실행 시간 변경
schedule.every().day.at("09:00").do(self.daily_job)  # 오전 9시
# schedule.every().day.at("00:00").do(self.daily_job)  # 자정
```

## 📝 로그 파일

- `theqoo_scheduler.log`: 스케줄러 실행 로그
- `theqoo_documents_YYYYMMDD.json`: 일별 수집된 문서

## 🔍 RAG 시스템 활용

저장된 벡터 데이터는 다음과 같이 활용할 수 있습니다:

```python
from qdrant_storage import QdrantStorage

storage = QdrantStorage()
results = storage.search_similar_documents("검색 쿼리", limit=5)

for result in results:
    print(f"제목: {result.payload['title']}")
    print(f"분석: {result.payload['analysis']}")
    print(f"유사도 점수: {result.score}")
```

## ⚠️ 주의사항

1. **API 사용량**: Perplexity API 호출 횟수에 주의하세요
2. **웹 크롤링**: Theqoo 사이트의 이용약관을 준수하세요
3. **저장 공간**: Qdrant 벡터 스토어의 저장 공간을 모니터링하세요
4. **네트워크**: 안정적인 인터넷 연결이 필요합니다

## 🐛 문제 해결

### Chrome 드라이버 오류
```bash
# webdriver-manager가 자동으로 관리하지만, 수동 설치가 필요한 경우:
pip install --upgrade webdriver-manager
```

### Qdrant 연결 오류
```bash
# Qdrant 서버 상태 확인
docker ps | grep qdrant
# 또는
curl http://localhost:6333/collections
```

### 메모리 부족 오류
- `max_comments` 값을 줄여보세요
- `end_idx - start_idx` 범위를 줄여보세요

### 환경변수 오류
```bash
# .env 파일이 올바른 위치에 있는지 확인
ls -la .env

# 환경변수 로드 확인
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('PERPLEXITY_API_KEY:', os.getenv('PERPLEXITY_API_KEY') is not None)"
```

## 📞 지원

문제가 발생하면 로그 파일을 확인하고, 필요시 이슈를 등록해주세요.

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 