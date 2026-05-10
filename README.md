# Cat Health Copilot 🐱

ESP32 기반 스마트 화장실 모니터링 시스템으로 고양이의 화장실 이용 패턴을 분석하여 건강 이상 징후를 감지합니다.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 시스템 개요

Cat Health Copilot은 ESP32 스마트 패드의 4개 로드셀 무게 데이터를 앱에서 해석하여 고양이 화장실 이용 패턴과 건강 이상 징후를 감지하는 비침습 펫 헬스케어 시스템입니다.

### ✨ 주요 기능

- **🎮 실시간 시뮬레이터**: 실제 센서 없이도 테스트 가능한 가상 시뮬레이터
  - 무게 감지 시작/종료 제어
  - 시간 경과 시뮬레이션 (+10초/+30초/+60초)
  - 무게 추가/감소 버튼으로 고양이 움직임 시뮬레이션
- **📊 이벤트 감지 및 분류**: 고양이 방문, 청소, 모래 보충 이벤트 자동 분류
- **🐈 고양이 개체 식별**: 체중 기반 다묘 환경 지원
- **📈 건강 패턴 분석**: 방문 빈도, 체류 시간, 체중 변화 추적
- **🔔 이상 징후 알림**: 평소와 다른 패턴 감지 시 보호자 알림
- **📱 대시보드**: 실시간 상태 및 분석 결과 시각화

## 🚀 빠른 시작

### Streamlit Cloud에서 바로 사용하기

[여기를 클릭](https://your-app-url.streamlit.app)하여 바로 사용해보세요!

### 로컬 설치

1. **저장소 클론**
```bash
git clone https://github.com/your-username/cat_health_copilot.git
cd cat_health_copilot
```

2. **가상 환경 생성 (권장)**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **실행**
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📖 사용 방법

### 1. 고양이 프로필 등록
- "고양이 프로필" 메뉴에서 고양이 정보 입력
- 이름, 체중, 나이, 성별 등 기본 정보 등록

### 2. 시뮬레이터로 테스트
- "실시간 시뮬레이션" 메뉴 선택
- 기준선 설정 (패드 + 모래 무게)
- 고양이 체중 설정
- "무게 감지됨" 버튼으로 방문 시작
- 시간 버튼으로 시간 경과 시뮬레이션
- 무게 추가/감소 버튼으로 움직임 시뮬레이션
- "무게 감지 안됨" 버튼으로 방문 종료

### 3. 결과 확인
- 홈 대시보드에서 오늘의 방문 횟수 확인
- 이벤트 타임라인에서 상세 기록 확인
- 고양이별 방문 통계 확인

## 🗂️ 프로젝트 구조

```
cat_health_copilot/
├── app.py                          # Streamlit 메인 애플리케이션
├── config/
│   ├── config.py                   # 설정 관리
│   └── thresholds.json             # 설정 파라미터
├── src/
│   ├── data/                       # 데이터 수신 및 검증
│   │   ├── receiver.py
│   │   ├── schema.py
│   │   └── validator.py
│   ├── preprocessing/              # 센서 전처리 및 baseline 관리
│   │   ├── filter.py
│   │   └── baseline.py
│   ├── events/                     # 이벤트 감지 및 분류
│   │   ├── detector.py
│   │   └── classifier.py
│   ├── identification/             # 고양이 식별
│   │   └── cat_identifier.py
│   └── storage/                    # 데이터 저장
│       └── database.py
├── data/                           # 데이터 저장 디렉토리
│   ├── raw/                        # 원본 센서 데이터
│   ├── processed/                  # 전처리된 데이터
│   ├── events/                     # 이벤트 기록
│   ├── profiles/                   # 고양이 프로필
│   ├── alerts/                     # 알림 기록
│   └── baseline/                   # 기준선 히스토리
└── requirements.txt                # Python 의존성
```

## ⚙️ 설정

`config/thresholds.json` 파일에서 다음 파라미터를 조정할 수 있습니다:

- **전처리**: 이동평균 윈도우, 노이즈 임계값
- **이벤트 감지**: 무게 변화 임계값, 최소/최대 이벤트 지속시간
- **분류**: 고양이 체중 범위, 방문 지속시간 범위

설정 페이지에서 GUI로도 조정 가능합니다.

## 🔄 데이터 초기화

팀원과 공유하거나 새로 시작하려면:

1. "설정" 메뉴로 이동
2. "전체 데이터 초기화" 버튼 클릭
3. 확인 후 모든 이벤트 및 센서 데이터 삭제
4. 고양이 프로필은 유지됨

## 📡 ESP32 데이터 형식

ESP32는 다음 형식의 JSON 데이터를 전송해야 합니다:

```json
{
  "device_id": "PAD_001",
  "timestamp": 1620000000000,
  "loadcell_1": 1.120,
  "loadcell_2": 1.080,
  "loadcell_3": 1.140,
  "loadcell_4": 1.090,
  "total_weight": 4.430
}
```

## ⚠️ 주의사항

- 이 시스템은 질병을 진단하지 않습니다
- 모든 알림은 관찰 기반이며 수의사 상담을 권장합니다
- 의료 진단 표현을 사용하지 않습니다

## 🤝 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📄 라이선스

MIT License

## 👥 팀

ESP32 기반 스마트 화장실 모니터링 시스템 개발팀

