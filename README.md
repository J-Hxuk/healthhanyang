# Cat Health Copilot

ESP32 기반 스마트 화장실 모니터링 시스템으로 고양이의 화장실 이용 패턴을 분석하여 건강 이상 징후를 감지합니다.

## 시스템 개요

Cat Health Copilot은 ESP32 스마트 패드의 4개 로드셀 무게 데이터를 앱에서 해석하여 고양이 화장실 이용 패턴과 건강 이상 징후를 감지하는 비침습 펫 헬스케어 시스템입니다.

### 주요 기능

- **실시간 센서 데이터 수집**: ESP32에서 4개 로드셀 무게 데이터 수신
- **이벤트 감지 및 분류**: 고양이 방문, 청소, 모래 보충 이벤트 자동 분류
- **고양이 개체 식별**: 체중 기반 다묘 환경 지원
- **건강 패턴 분석**: 방문 빈도, 체류 시간, 체중 변화 추적
- **이상 징후 알림**: 평소와 다른 패턴 감지 시 보호자 알림
- **대시보드**: 실시간 상태 및 분석 결과 시각화

## 설치 방법

### 1. 가상 환경 생성 (권장)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 프로젝트 구조

```
cat_health_copilot/
├── app.py                          # Streamlit 메인 애플리케이션
├── config/
│   └── thresholds.json             # 설정 파라미터
├── src/
│   ├── data/                       # 데이터 수신 및 검증
│   ├── preprocessing/              # 센서 전처리 및 baseline 관리
│   ├── events/                     # 이벤트 감지 및 분류
│   ├── identification/             # 고양이 식별
│   ├── analysis/                   # 건강 분석 및 알림
│   ├── storage/                    # 데이터 저장
│   └── ui/                         # UI 컴포넌트
├── data/                           # 데이터 저장 디렉토리
├── tests/                          # 테스트 코드
└── requirements.txt                # Python 의존성
```

## 설정

`config/thresholds.json` 파일에서 다음 파라미터를 조정할 수 있습니다:

- **전처리**: 이동평균 윈도우, 노이즈 임계값
- **이벤트 감지**: 무게 변화 임계값, 최소/최대 이벤트 지속시간
- **분류**: 고양이 체중 범위, 방문 지속시간 범위
- **건강 분석**: 경고/위험 임계값

## ESP32 데이터 형식

ESP32는 다음 형식의 JSON 데이터를 전송해야 합니다:

```json
{
  "device_id": "PAD_001",
  "timestamp": 15200,
  "loadcell_1": 1.120,
  "loadcell_2": 1.080,
  "loadcell_3": 1.140,
  "loadcell_4": 1.090,
  "total_weight": 4.430
}
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# Property-based 테스트만 실행
pytest tests/property/

# 특정 테스트 파일 실행
pytest tests/unit/test_database.py
```

## 주의사항

- 이 시스템은 질병을 진단하지 않습니다
- 모든 알림은 관찰 기반이며 수의사 상담을 권장합니다
- 의료 진단 표현을 사용하지 않습니다

## 라이선스

MIT License
