import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os

# load_to_csv.py에서 SQL문 수정 후, 필요한 CSV 파일 가져오기
# 가게 주소로부터 좌표 얻기 (카카오 로컬 API 사용)
# 주소에 대한 좌표가 없으면 lat, lng 칼럼에 None 저장
# 프로그램 작동 하기 전에
# SELECT s_idx, s_name, s_address FROM store WHERE s_location = '서울대 입구역' AND s_address NOT LIKE '서울%';
# 등을 통해 주소 데이터 점검 권장

# 입력 파일: store_addr_전북대.csv
# 출력 파일: coord_included.csv

load_dotenv()
KAKAO_API_KEY = os.environ.get("KAKAO_API_KEY")

def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    params = {"query": address}
    res = requests.get(url, headers=headers, params=params)
    return res.json()

test_data = pd.read_csv("store_addr_부산대.csv", encoding="utf-8")

test_data["lat"] = None  # 위도
test_data["lng"] = None  # 경도

for i in range(len(test_data)):
    addr = test_data.loc[i, "s_address"]

    # [ ] 제거
    if isinstance(addr, str) and addr.endswith("]"):
        addr = addr.split("[")[0]
        test_data.loc[i, "s_address"] = addr

    try:
        api_json = get_location(addr)

        if api_json["documents"]:
            address = api_json["documents"][0]["address"]
            test_data.loc[i, "lat"] = address["y"]
            test_data.loc[i, "lng"] = address["x"]
        else:
            test_data.loc[i, "lat"] = None
            test_data.loc[i, "lng"] = None

        print(f"{i}번째 변환 완료")

        time.sleep(0.15)  # ⭐ API 제한 대비

    except Exception as e:
        print(f"{i}번째 오류:", e)
        time.sleep(1)

test_data.to_csv("coord_included.csv", encoding="utf-8-sig", index=False)