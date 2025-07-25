import requests
from bs4 import BeautifulSoup
import json

query_keyword = "에어프레미아"
url = f'https://www.youtube.com/results?search_query={query_keyword}&sp=EgQIAhAB'
# url = "https://www.youtube.com/results?search_query=%EC%86%90%ED%9D%A5%EB%AF%BC"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# JSON 데이터 추출
script_tags = soup.find_all('script')
initial_data = None

for script in script_tags:
    if script.string and 'var ytInitialData =' in script.string:
        json_str = script.string.split('var ytInitialData = ')[1].split('};')[0] + '}'
        initial_data = json.loads(json_str)
        break
# print(initial_data)
# 동영상 정보 추출
# videos = []
# contents = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
#
# for item in contents:
#     if 'videoRenderer' in item:
#         video = item['videoRenderer']
#         title = video['title']['runs'][0]['text']
#         video_id = video['videoId']
#         href = f'https://www.youtube.com/watch?v={video_id}'
#         videos.append({'title': title, 'href': href})
#
# print("추출된 동영상:")
# for video in videos[:10]:  # 상위 10개 출력
#     print(f"- 제목: {video['title']}\n  링크: {video['href']}\n")

# 동영상 & 숏츠 정보 추출
videos = []
contents = \
initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0][
    'itemSectionRenderer']['contents']

for item in contents:
    print(item)
    # 일반 동영상인 경우
    if 'videoRenderer' in item:
        video = item['videoRenderer']
        title = video['title']['runs'][0]['text']
        video_id = video['videoId']
        href = f'https://www.youtube.com/watch?v={video_id}'
        videos.append({'type': 'video', 'title': title, 'href': href})

        # # 타입 판별 로직
        # video_type = 'video'
        # href = f'https://www.youtube.com/watch?v={video_id}'
        #
        # # 방법1: navigationEndpoint 체크
        # if 'navigationEndpoint' in video:
        #     endpoint = video['navigationEndpoint']
        #     if 'reelWatchEndpoint' in endpoint:
        #         # video_type = 'shorts'
        #         href = f'https://www.youtube.com/shorts/{video_id}'
        #         videos.append({'type': 'shorts', 'title': title, 'href': href})

    # 숏츠(Shorts)인 경우
    elif 'reelWatchEndpoint' in item:
        # print(item)
        short = item['reelWatchEndpoint']
        title = short['headline']['simpleText']  # 숏츠 제목 경로가 다름
        video_id = short['videoId']
        href = f'https://www.youtube.com/shorts/{video_id}'  # 숏츠 전용 URL
        videos.append({'type': 'shorts', 'title': title, 'href': href})

print("추출된 콘텐츠:")
for content in videos[:30]:  # 상위 15개 출력 (숏츠 포함)
    print(f"- [{content['type'].upper()}] {content['title']}\n  링크: {content['href']}\n")
