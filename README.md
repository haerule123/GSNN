# GSNN (감정 기반 맛집 추천)

네이버 지도 리뷰 데이터를 수집·정제하고, **DistilKoBERT(KoBERT 계열) 기반 6개 이진 분류 모델(5감정 + 불만) 앙상블**로 리뷰 감정을 점수화한 뒤  
사용자의 **현재 감정/상황(텍스트 입력, 날씨, 운세)**에 맞춰 맛집을 추천하는 Flask 웹서비스입니다.

데이터 수집 → 감정 분석 → DB 집계 → 추천/웹서비스까지 한 흐름으로 구성했습니다.

---

## 프로젝트 개요
대학 상권에서 “지금 기분/상황에 맞는 선택”은 중요한데, 기존 추천은 평점·카테고리 중심이라 개인 상태를 반영하기 어렵습니다.

GSNN은
- **리뷰 기반 감정 점수(DB 집계)**
- **사용자 상태 신호(감정 텍스트/날씨/운세)**

를 결합해, “지금의 나”에 맞춘 추천을 제공하는 것을 목표로 합니다.

---

## 핵심 기능
- 감정 기반 추천: 사용자 문장 입력 → Gemini 감정 분류(희/노/애(슬픔)/애(사랑)/락) → 감정 점수 상위 가게 추천
- 날씨 기반 추천: OpenWeather 실시간 날씨 → 정해진 룰 기반 카테고리 우선순위 → 카테고리별 추천
- 운세 기반 추천(로그인 연동): 생년월일 기반 운세 텍스트 + 추천 카테고리 3개 생성(Gemini)
- 가게 상세 페이지: 메뉴/주소/좌표/감정 점수, 월별 감정 변화 분석표 제공
- 회원 기능: 회원가입/로그인/마이페이지/비밀번호 변경
- 데이터 파이프라인: 크롤링 → 라벨링(앙상블) → DB 적재 → 집계 테이블로 추천 성능/속도 개선

---

## 폴더 구조
```text
GSNN/
├─ crawler/
│  ├─ naver_review.py            # 네이버 지도 리뷰 수집
│  ├─ store_list.py              # 가게 목록 수집/관리
│  ├─ load_to_csv.py             # emotion 없는 리뷰 → CSV 추출
│  ├─ load_csv_to_db.py          # 라벨링 CSV → emotion 테이블 적재
│  ├─ update_coord_to_db.py      # 좌표 업데이트
│  ├─ get_coord_from_csv.py      # CSV 기반 좌표 처리
│  ├─ LinuxMySQL.txt             # 스키마/집계 테이블 SQL 문서
│  └─ DBManager.py               # DB 유틸
├─ front/
│  ├─ app.py                     # Flask 엔트리
│  ├─ service.py                 # 추천/비즈니스 로직
│  ├─ user_service.py            # 사용자 관련 로직
│  ├─ weather.py                 # 날씨 API
│  ├─ reco_based_on_weather.py   # 날씨 기반 추천 로직
│  ├─ gemini_api.py              # LLM API 연동
│  ├─ gemini_one_line.py         # 리뷰 기반 한줄평 생성
│  ├─ templates/                 # HTML 템플릿
│  └─ static/                    # 정적 파일 (CSS/JS/이미지)
└─ machine_learning_final/
   └─ machine-learning/
      ├─ model_*.py              # 감정별 모델 학습
      ├─ ensemble_biased.py      # 앙상블 추론/분석
      ├─ ensemble_biased_labling.py # 리뷰 CSV 라벨링 파이프라인
      ├─ raw/                    # 학습/평가 데이터
      └─ EMOTION_RESULT/         # 감정 분석 결과 산출물
```

---

## 아키텍처 요약
```
Browser (Jinja2 HTML/CSS/JS)
  → Flask (front/app.py)
	  → DB Query/조립 (front/service.py)
	  → LLM (front/gemini_api.py)
	  → Weather Rule (front/reco_based_on_weather.py)
	  → MySQL

Crawler (crawler/*) → MySQL
ML (machine_learning_final/*) → emotion 점수 산출 → MySQL
```

---

## 데이터 파이프라인(수집 → 라벨링 → 집계)
1) `crawler/store_list.py` : 상권(대학) 기준 가게 목록 수집 → `store`
2) `crawler/naver_review.py` : 이미지/주소/메뉴/리뷰 수집(트랜잭션) → `store/menu/review`
3) `crawler/load_to_csv.py` : `emotion`이 없는 리뷰만 추출 → `review.csv`
4) `machine_learning_final/machine-learning/ensemble_biased_labling.py` : 리뷰별 6개 점수 산출(앙상블)
5) `crawler/load_csv_to_db.py` : 라벨링 CSV → `emotion` insert
6) `store_emotion_count_table` : 가게별 대표 감정 집계(추천 정렬/필터에 사용)

---

## 로컬 실행

### 1) 환경변수(.env)
프로젝트 루트에 `.env`를 생성하세요(크롤러/웹에서 공통 사용).

```env
SECRET_KEY=your-secret

host=127.0.0.1
port=3306
user=root
passwd=your-password
dbname=bigdata

GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-flash
OPEN_WEATHER_API=your-openweather-key
KAKAO_API_KEY=your-kakao-key
```

### 2) 패키지 설치(웹서비스)
```bash
pip install flask pandas python-dotenv pymysql mysql-connector-python requests google-genai
```

### 3) Flask 실행
```bash
cd front
python app.py
```

> DB 스키마/집계 테이블 생성 SQL은 `crawler/LinuxMySQL.txt` 참고

---

## 파일별 역할(핵심)

### front/
- `app.py`: Flask 라우팅(감정/날씨/운세 추천, 상세 페이지, 회원 API)
- `service.py`: 추천/상세/월별 감정 데이터 등 DB 쿼리 + 결과 조립
- `gemini_api.py`: 감정 분석(희/노/슬/사/락), 운세+카테고리 추천
- `reco_based_on_weather.py`: OpenWeather 조회 + 룰 기반 카테고리 우선순위
- `weather.py`: (대안) 날씨 → Gemini 프롬프트로 카테고리 추천(LLM)
- `templates/`: 화면 템플릿, `static/`: CSS/JS/이미지

### crawler/
- `store_list.py`: 가게 목록 수집(네이버 지도 검색)
- `naver_review.py`: 가게 상세(이미지/주소/메뉴/리뷰) 수집 + 트랜잭션 저장
- `load_to_csv.py`: emotion 없는 리뷰 추출 CSV
- `load_csv_to_db.py`: 라벨링 결과를 `emotion` 테이블로 적재
- `get_coord_from_csv.py` / `update_coord_to_db.py`: 좌표 생성 및 DB 반영(Kakao Local)

### machine_learning_final/
- `model_*.py`: 감정별 학습 스크립트
- `ensemble_biased*.py`: 앙상블 추론/라벨링 파이프라인

---

## DB 요약
핵심 테이블: `store`, `menu`, `review`, `etype`, `emotion`, `store_emotion_count_table`

---

## 알려진 이슈 / TODO
- `front/app.py`에 `/favorites` 라우트가 있으나 템플릿이 현재 포함되어 있지 않습니다.
- 크롤링은 Selenium/Chrome 버전 호환에 민감합니다.
