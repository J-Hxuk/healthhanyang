# ESP32 센서 연동 가이드

## 개요

ESP32에서 로드셀 센서 데이터를 Flask 서버로 전송하고, 시스템에서 처리하는 방법을 설명합니다.

## 시스템 구조

```
ESP32 (로드셀 센서)
    ↓ HTTP POST (JSON)
Flask 서버 (flask_server.py)
    ↓ 데이터 변환 및 처리
데이터 파이프라인
    ↓
Streamlit 대시보드
```

## ESP32 데이터 형식

ESP32는 다음 형식으로 데이터를 전송합니다:

```json
{
  "loadcell1": 12345,
  "loadcell2": 23456,
  "loadcell3": 34567,
  "loadcell4": 45678,
  "total": 115746
}
```

**참고**: 이 값들은 raw 값이며, 보정 전에는 실제 kg 단위가 아닙니다.

## Flask 서버 실행

### 1. 서버 시작

```bash
python flask_server.py
```

서버가 `http://0.0.0.0:5000`에서 실행됩니다.

### 2. 네트워크 IP 확인

ESP32가 접속할 수 있도록 노트북의 IP 주소를 확인합니다:

**Windows**:
```bash
ipconfig
```

**Mac/Linux**:
```bash
ifconfig
```

예: `192.168.0.10` 또는 `172.20.10.5`

### 3. ESP32 코드 업데이트

ESP32 코드의 `serverUrl`을 노트북 IP로 변경:

```cpp
const char* serverUrl = "http://YOUR_LAPTOP_IP:5000/data";
// 예: "http://172.20.10.5:5000/data"
```

## 로드셀 보정

### 보정이 필요한 이유

로드셀 센서는 raw 값을 출력하므로, 실제 무게(kg)로 변환하려면 보정이 필요합니다.

### 보정 방법

1. **알려진 무게 준비**: 정확한 무게를 아는 물체 (예: 5kg 아령)

2. **Raw 값 확인**: ESP32 시리얼 모니터에서 해당 무게의 raw 값 확인
   ```
   Total: 123456
   ```

3. **보정 API 호출**:

```bash
curl -X POST http://localhost:5000/calibrate \
  -H "Content-Type: application/json" \
  -d '{
    "raw_value": 123456,
    "known_weight_kg": 5.0
  }'
```

**응답**:
```json
{
  "status": "success",
  "calibration_factor": 0.0000405,
  "message": "Calibration factor set to 0.0000405"
}
```

4. **보정 확인**: 다른 무게를 올려서 정확한지 확인

### 보정 계수 저장

보정 계수는 서버 재시작 시 초기화됩니다. 영구 저장하려면:

1. `flask_server.py`의 초기화 부분 수정:
```python
esp32_adapter = ESP32DataAdapter(
    device_id="esp32_001", 
    calibration_factor=0.0000405  # 보정된 값으로 변경
)
```

2. 또는 설정 파일로 관리:
```python
# config/sensor_config.json
{
  "device_id": "esp32_001",
  "calibration_factor": 0.0000405
}
```

## API 엔드포인트

### 1. 데이터 수신
- **URL**: `POST /data`
- **설명**: ESP32에서 센서 데이터 수신
- **요청 형식**:
```json
{
  "loadcell1": 12345,
  "loadcell2": 23456,
  "loadcell3": 34567,
  "loadcell4": 45678,
  "total": 115746
}
```
- **응답**:
```json
{
  "status": "success",
  "message": "Data processed successfully",
  "data_id": "uuid-here",
  "total_weight": 5.123,
  "baseline": 4.567
}
```

### 2. 보정
- **URL**: `POST /calibrate`
- **설명**: 로드셀 보정 계수 설정
- **요청 형식**:
```json
{
  "raw_value": 123456,
  "known_weight_kg": 5.0
}
```

### 3. 상태 확인
- **URL**: `GET /status`
- **설명**: 서버 상태 및 보정 정보 확인
- **응답**:
```json
{
  "status": "running",
  "timestamp": "2024-01-15T10:30:00",
  "calibration_factor": 0.0000405,
  "device_id": "esp32_001"
}
```

## 데이터 처리 파이프라인

Flask 서버가 데이터를 받으면 다음 순서로 처리됩니다:

1. **ESP32 어댑터**: raw 값을 시스템 형식으로 변환
2. **수신기**: 데이터 검증
3. **노이즈 필터**: 센서 노이즈 제거
4. **기준선 관리자**: 기준선 업데이트
5. **이벤트 감지기**: 입실/퇴실 이벤트 감지
6. **이벤트 분류기**: 이벤트 타입 분류
7. **고양이 식별기**: 고양이 개체 식별
8. **체중 추적기**: 체중 기록 및 추적
9. **알림 생성기**: 체중 변화 알림 생성

## 문제 해결

### ESP32가 서버에 연결되지 않음

1. **Wi-Fi 연결 확인**:
   - ESP32와 노트북이 같은 Wi-Fi에 연결되어 있는지 확인
   - ESP32 시리얼 모니터에서 "WiFi connected!" 메시지 확인

2. **IP 주소 확인**:
   - Flask 서버 실행 시 표시되는 IP 주소 확인
   - ESP32 코드의 `serverUrl`과 일치하는지 확인

3. **방화벽 확인**:
   - Windows 방화벽에서 포트 5000 허용
   - 바이러스 백신 소프트웨어 확인

### 데이터가 처리되지 않음

1. **Flask 서버 로그 확인**:
```bash
python flask_server.py
```
   - 에러 메시지 확인

2. **데이터 형식 확인**:
   - ESP32 시리얼 모니터에서 전송되는 JSON 형식 확인
   - `Sent data: {...}` 메시지 확인

3. **보정 계수 확인**:
```bash
curl http://localhost:5000/status
```

### 체중 값이 이상함

1. **보정 필요**: 로드셀 보정 수행
2. **센서 연결 확인**: 로드셀 4개가 모두 제대로 연결되었는지 확인
3. **영점 조정**: 빈 화장실 상태에서 영점 조정

## 다음 단계

1. ✅ Flask 서버 실행
2. ✅ ESP32 연결 확인
3. ✅ 데이터 수신 확인
4. ⬜ 로드셀 보정
5. ⬜ Streamlit 대시보드에서 실시간 데이터 확인
6. ⬜ 고양이 프로필 등록
7. ⬜ 이벤트 감지 테스트

## 참고

- ESP32 코드: 프로젝트 루트의 `esp32_code.ino` 참조
- Streamlit 대시보드: `streamlit run app.py`
- 데이터 저장 위치: `data/raw/`, `data/processed/`, `data/events/`
