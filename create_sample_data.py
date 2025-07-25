#!/usr/bin/env python3
"""
RAG 시스템 테스트를 위한 샘플 데이터 생성 스크립트
"""

import json
from datetime import datetime

def create_sample_data():
    """샘플 데이터 생성"""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    sample_documents = [
        {
            "title": "최신 AI 기술 동향과 미래 전망",
            "link": "https://theqoo.net/ai_tech_2024",
            "page_num": 2,
            "post_datetime": "2024-01-15 14:30:00",
            "content": "최근 AI 기술이 급속도로 발전하고 있습니다. GPT-4, Claude, Gemini 등 다양한 대형 언어 모델이 등장하면서 AI의 활용 범위가 크게 확장되었습니다. 특히 생성형 AI는 텍스트, 이미지, 음성, 비디오 등 다양한 형태의 콘텐츠를 생성할 수 있게 되었습니다. 이는 교육, 의료, 엔터테인먼트, 비즈니스 등 거의 모든 분야에 혁신을 가져올 것으로 예상됩니다.",
            "comments": [
                "AI 기술이 정말 놀라워요. 앞으로 어떻게 발전할지 궁금합니다.",
                "생성형 AI의 윤리적 문제도 고려해야 할 것 같아요.",
                "AI가 일자리를 대체할까봐 걱정이에요.",
                "AI를 활용한 새로운 비즈니스 모델이 많이 나올 것 같아요.",
                "교육 분야에서 AI 활용이 활발해지고 있네요."
            ],
            "comments_count": 5,
            "analysis": "AI 기술의 최신 동향과 미래 전망에 대한 종합적인 분석입니다. 생성형 AI의 발전과 다양한 분야에서의 활용 가능성, 그리고 윤리적 고려사항까지 다루고 있습니다. 특히 GPT-4, Claude, Gemini 등 주요 AI 모델들의 등장과 그 영향에 대해 자세히 설명하고 있습니다.",
            "collected_date": current_date,
            "id": f"theqoo_{current_date}_1"
        },
        {
            "title": "2024년 게임 업계 트렌드 분석",
            "link": "https://theqoo.net/gaming_trends_2024",
            "page_num": 3,
            "post_datetime": "2024-01-16 09:15:00",
            "content": "2024년 게임 업계는 다양한 변화를 맞이하고 있습니다. 모바일 게임의 지속적인 성장, 클라우드 게이밍의 확산, 메타버스 게임의 등장 등이 주요 트렌드입니다. 특히 AI 기술을 활용한 게임 개발이 활발해지고 있으며, 플레이어의 행동을 분석하여 개인화된 게임 경험을 제공하는 기술이 주목받고 있습니다.",
            "comments": [
                "모바일 게임이 정말 많이 발전했어요.",
                "클라우드 게이밍은 아직 네트워크 문제가 있지만 미래가 밝아 보여요.",
                "메타버스 게임은 아직 초기 단계인 것 같아요.",
                "AI가 게임 개발에 활용되는 것이 흥미롭네요.",
                "개인화된 게임 경험이 정말 중요한 것 같아요."
            ],
            "comments_count": 5,
            "analysis": "2024년 게임 업계의 주요 트렌드를 종합적으로 분석한 내용입니다. 모바일 게임, 클라우드 게이밍, 메타버스 게임, AI 활용 등 다양한 측면에서 게임 업계의 변화를 다루고 있습니다. 특히 AI 기술의 게임 개발 활용과 개인화된 게임 경험 제공에 대한 전망을 제시하고 있습니다.",
            "collected_date": current_date,
            "id": f"theqoo_{current_date}_2"
        },
        {
            "title": "환경 보호와 지속가능한 발전",
            "link": "https://theqoo.net/environment_sustainability",
            "page_num": 4,
            "post_datetime": "2024-01-17 16:45:00",
            "content": "기후 변화와 환경 문제가 전 세계적으로 중요한 이슈가 되고 있습니다. 탄소 중립, 재생 에너지 확대, 플라스틱 사용 감소 등 다양한 환경 보호 활동이 진행되고 있습니다. 개인과 기업, 정부 모두가 함께 노력해야 하는 문제이며, 지속가능한 발전을 위한 구체적인 실천 방안들이 제시되고 있습니다.",
            "comments": [
                "환경 보호는 정말 중요한 문제예요.",
                "재생 에너지 사용을 늘려야겠어요.",
                "플라스틱 사용을 줄이는 것이 중요해요.",
                "기업의 환경 책임도 중요합니다.",
                "개인 차원에서 할 수 있는 일들이 많아요."
            ],
            "comments_count": 5,
            "analysis": "환경 보호와 지속가능한 발전에 대한 종합적인 논의입니다. 기후 변화, 탄소 중립, 재생 에너지, 플라스틱 사용 감소 등 다양한 환경 이슈를 다루고 있으며, 개인, 기업, 정부의 역할과 구체적인 실천 방안을 제시하고 있습니다.",
            "collected_date": current_date,
            "id": f"theqoo_{current_date}_3"
        },
        {
            "title": "디지털 헬스케어의 발전과 미래",
            "link": "https://theqoo.net/digital_healthcare",
            "page_num": 5,
            "post_datetime": "2024-01-18 11:20:00",
            "content": "디지털 헬스케어 기술이 빠르게 발전하고 있습니다. 웨어러블 디바이스, 원격 진료, AI 진단, 디지털 치료제 등 다양한 기술이 의료 분야에 적용되고 있습니다. 특히 코로나19 이후 원격 진료의 필요성이 증가하면서 디지털 헬스케어의 중요성이 더욱 부각되고 있습니다.",
            "comments": [
                "웨어러블 디바이스로 건강을 모니터링하는 것이 편리해요.",
                "원격 진료가 정말 유용한 것 같아요.",
                "AI 진단의 정확성이 궁금해요.",
                "디지털 치료제는 어떤 것인가요?",
                "개인정보 보호가 중요한 것 같아요."
            ],
            "comments_count": 5,
            "analysis": "디지털 헬스케어의 발전과 미래 전망에 대한 종합적인 분석입니다. 웨어러블 디바이스, 원격 진료, AI 진단, 디지털 치료제 등 다양한 디지털 헬스케어 기술을 다루고 있으며, 코로나19 이후의 변화와 향후 전망을 제시하고 있습니다.",
            "collected_date": current_date,
            "id": f"theqoo_{current_date}_4"
        },
        {
            "title": "교육의 디지털 전환과 온라인 학습",
            "link": "https://theqoo.net/digital_education",
            "page_num": 6,
            "post_datetime": "2024-01-19 13:10:00",
            "content": "교육 분야에서도 디지털 전환이 활발하게 진행되고 있습니다. 온라인 강의, AI 튜터, 개인화 학습, 가상현실 교육 등 다양한 디지털 교육 기술이 등장하고 있습니다. 특히 코로나19 이후 원격 교육의 필요성이 증가하면서 교육의 디지털화가 가속화되었습니다.",
            "comments": [
                "온라인 강의가 정말 편리해요.",
                "AI 튜터가 개인별 맞춤 학습을 도와주는 것이 좋아요.",
                "가상현실 교육이 흥미롭네요.",
                "온라인 교육의 한계도 있는 것 같아요.",
                "교사와 학생 간의 소통이 중요해요."
            ],
            "comments_count": 5,
            "analysis": "교육의 디지털 전환과 온라인 학습에 대한 종합적인 논의입니다. 온라인 강의, AI 튜터, 개인화 학습, 가상현실 교육 등 다양한 디지털 교육 기술을 다루고 있으며, 코로나19 이후의 변화와 교육의 미래를 제시하고 있습니다.",
            "collected_date": current_date,
            "id": f"theqoo_{current_date}_5"
        }
    ]
    
    # JSON 파일로 저장
    filename = f"sample_documents_{current_date}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_documents, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 샘플 데이터가 {filename}에 저장되었습니다.")
    print(f"📊 총 {len(sample_documents)}개의 문서가 생성되었습니다.")
    
    return filename

def main():
    """메인 함수"""
    print("RAG 시스템 테스트를 위한 샘플 데이터를 생성합니다...")
    
    filename = create_sample_data()
    
    print(f"\n이제 다음 명령어로 RAG 시스템을 테스트할 수 있습니다:")
    print(f"python rag_chat_system.py")
    print(f"\n생성된 파일: {filename}")

if __name__ == "__main__":
    main() 