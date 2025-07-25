import streamlit as st
from openai import OpenAI

# 페이지 레이아웃 설정
st.set_page_config(page_title="기업 분석 리포트", layout="wide")


# 사용자 정의 함수 예시 (실제 구현 필요)
def process_company(company_name):
    """사용자가 구현해야 할 커스텀 처리 함수"""
    # 여기에 실제 비즈니스 로직 구현
    return {
        'summary': f"{company_name}의 주요 업무 및 시장 동향 분석",
        'data_points': ["시장 점유율", "최근 투자 현황", "경쟁사 비교"]
    }


# 사이드바에 API 키 입력
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("OpenAI API 키", type="password")
    st.markdown("---")

# 메인 화면 구성
st.title("📈 기업 분석 리포트 생성기")

# 회사명 입력 (옵셔널)
company_name = st.text_input("분석할 회사명을 입력하세요 (선택사항)", "")

# 처리 버튼 및 결과 표시
if st.button("분석 시작"):
    if not api_key:
        st.error("❌ OpenAI API 키를 입력해주세요")
        st.stop()

    try:
        # 사용자 정의 함수 실행
        processed_data = process_company(company_name) if company_name else process_company("")

        # GPT 프롬프트 생성
        prompt = f"""
        다음 정보를 바탕으로 전문적인 분석 보고서를 작성해주세요:
        {processed_data}

        요구사항:
        1. 3단락 이내의 간결한 요약문
        2. 핵심 키워드 5개(해시태그 형식)
        3. JSON 형식으로 응답 (content, keywords 필드 포함)
        """

        # OpenAI API 호출
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        # 결과 파싱
        result = eval(response.choices[0].message.content)

        # 결과 표시
        with st.expander("📄 전체 분석 보고서", expanded=True):
            st.write(result['content'])

        # 키워드 표시
        st.subheader("🔑 주요 키워드")
        cols = st.columns(5)
        for i, keyword in enumerate(result['keywords'][:5]):
            cols[i].success(f"#{keyword}")

    except Exception as e:
        st.error(f"⚠️ 오류 발생: {str(e)}")
