# 구현 계획: 고급 시뮬레이션 및 추적 기능

## 개요

이 구현 계획은 Cat Health Copilot 시스템에 고급 시뮬레이션 및 추적 기능을 추가합니다. 주요 기능은 다음과 같습니다:

1. **체중 변화 추적**: 시간 경과에 따른 고양이 체중 모니터링 및 추세 분석
2. **알림 생성**: 체중 변화 및 방문 패턴 기반 자동 건강 알림
3. **기준선 변동 시뮬레이션**: 실제와 유사한 화장실 무게 변화
4. **장기 시뮬레이션**: 테스트를 위한 다일 시나리오 생성
5. **실제 센서 통합**: 시뮬레이션 및 물리적 센서 데이터 모두 지원

구현은 기존 이벤트 기반 아키텍처를 확장하며, 시뮬레이션과 실제 센서 데이터가 동일한 처리 파이프라인을 통과하도록 보장합니다.

## 작업 목록

- [ ] 1. 데이터 모델 확장 및 데이터베이스 스토리지 구현
  - [x] 1.1 WeightMeasurement 데이터 모델 추가
    - `src/data/schema.py`에 `WeightMeasurement` 데이터클래스 추가
    - 필드: measurement_id, cat_id, event_id, measured_weight, profile_weight, weight_difference, timestamp, data_source
    - `to_dict()` 및 `from_dict()` 메서드 구현
    - _요구사항: 1.1, 1.4_
  
  - [x] 1.2 DataSourceMode 열거형 추가
    - `src/data/schema.py`에 `DataSourceMode` 열거형 추가 (SIMULATION, SENSOR)
    - 기존 `Event` 모델에 `data_source: DataSourceMode` 필드 추가
    - _요구사항: 11.2, 11.10_
  
  - [ ] 1.3 BaselineHistory 모델 확장
    - `src/data/schema.py`의 `BaselineHistory`에 필드 추가: previous_weight, change_amount, data_source
    - `to_dict()` 및 `from_dict()` 메서드 업데이트
    - _요구사항: 8.2_
  
  - [~] 1.4 SensorConnectionInfo 데이터 모델 추가
    - `src/data/schema.py`에 `ConnectionStatus` 열거형 추가 (CONNECTED, DISCONNECTED, ERROR)
    - `SensorConnectionInfo` 데이터클래스 추가
    - 필드: device_id, status, last_received, last_weight, connection_time, error_message
    - _요구사항: 11.6, 11.12_
  
  - [~] 1.5 SimulationResult 데이터 모델 추가
    - `src/data/schema.py`에 `SimulationScenario` 열거형 추가 (NORMAL, POLYURIA_ONSET, GRADUAL_WEIGHT_LOSS, COMBINED)
    - `SimulationConfig` 및 `SimulationResult` 데이터클래스 추가
    - _요구사항: 4.3, 6.3_
  
  - [~] 1.6 Database 클래스에 체중 측정 스토리지 추가
    - `src/storage/database.py`에 `save_weight_measurement()` 메서드 추가
    - `get_weight_history()` 메서드 추가 (cat_id, start_date, end_date 필터링 지원)
    - `get_latest_measurement()` 메서드 추가
    - data/weight_history 디렉토리 생성
    - _요구사항: 1.4, 1.5_

- [ ] 2. WeightTracker 컴포넌트 구현
  - [~] 2.1 WeightTracker 클래스 생성
    - `src/tracking/weight_tracker.py` 파일 생성
    - `WeightTracker` 클래스 구현 (database 의존성)
    - `record_measurement()` 메서드: 이벤트에서 체중 측정 기록
    - 측정 체중 계산: `event.avg_weight - event.baseline_before`
    - _요구사항: 1.1, 1.2_
  
  - [~] 2.2 체중 변화율 계산 기능 구현
    - `calculate_weight_change_rate()` 메서드 추가 (cat_id, days 파라미터)
    - 지정된 기간 동안의 체중 변화율(백분율) 계산
    - 측정값이 부족한 경우 None 반환
    - _요구사항: 1.3_
  
  - [~] 2.3 체중 히스토리 조회 기능 구현
    - `get_weight_history()` 메서드 구현
    - 날짜 범위 필터링 지원
    - 시간순 정렬 반환
    - _요구사항: 1.5_

- [ ] 3. AlertGenerator 컴포넌트 구현
  - [~] 3.1 AlertGenerator 클래스 생성
    - `src/alerts/alert_generator.py` 파일 생성
    - `WeightChangeAlert` 데이터클래스 추가
    - `AlertGenerator` 클래스 구현 (database, weight_tracker 의존성)
    - 중복 알림 방지를 위한 alert_cache 초기화
    - _요구사항: 2.4_
  
  - [~] 3.2 체중 변화 알림 임계값 검사 구현
    - `should_create_alert()` 메서드 구현
    - 경고 조건: 7일 동안 5% 초과
    - 위험 조건: 7일 동안 10% 초과 또는 7일 미만 기간에 7.5% 초과
    - 심각도 수준 반환 (warning/critical) 또는 None
    - _요구사항: 2.1, 2.2, 2.3_
  
  - [~] 3.3 알림 생성 및 중복 방지 구현
    - `create_alert()` 메서드 구현
    - 알림 정보 포함: 고양이 이름, 프로필 체중, 현재 체중, 변화율, 기간, 권장 조치
    - `is_duplicate_alert()` 메서드 구현 (24시간 내 중복 확인)
    - `check_weight_change_alerts()` 메서드 구현 (전체 흐름 조율)
    - _요구사항: 2.4, 2.5, 2.6_

- [~] 4. 체크포인트 - 핵심 추적 기능 테스트
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의하세요.

- [ ] 5. DataSourceInterface 및 센서 연결 구현
  - [~] 5.1 DataSourceInterface 클래스 생성
    - `src/data/data_source_interface.py` 파일 생성
    - `DataSourceInterface` 클래스 구현
    - 모드 전환 메서드: `set_mode(mode: DataSourceMode)`
    - 데이터 가져오기 메서드: `get_data() -> Optional[RawSensorData]`
    - 연결 상태 확인: `get_connection_status()`, `is_available()`
    - _요구사항: 11.1, 11.2, 11.8_
  
  - [~] 5.2 SensorConnection 클래스 구현
    - `src/data/sensor_connection.py` 파일 생성
    - `SensorConnection` 클래스 구현
    - 연결 관리: `connect()`, `disconnect()`, `receive_data()`
    - 상태 모니터링: `update_status()` (30초 타임아웃 기반)
    - 데이터 형식 검증
    - _요구사항: 11.3, 11.4, 11.5, 11.6, 11.14_
  
  - [~] 5.3 SimulationGenerator 클래스 구현
    - `src/simulation/simulation_generator.py` 파일 생성
    - `SimulationGenerator` 클래스 구현
    - 상태 관리: baseline_weight, current_weight, cat_on_pad
    - 시뮬레이션 제어: `simulate_cat_entry()`, `simulate_cat_exit()`, `add_weight_variation()`
    - 데이터 포인트 생성: `generate_data_point()` (현실적인 노이즈 포함)
    - _요구사항: 11.2_
  
  - [~] 5.4 Receiver에 DataSourceInterface 통합
    - `src/data/receiver.py` 수정
    - 직접 센서 입력 대신 DataSourceInterface 사용
    - 데이터 소스에 관계없이 동일한 처리 파이프라인 유지
    - _요구사항: 11.2, 11.11_

- [ ] 6. BaselineSimulator 컴포넌트 구현
  - [~] 6.1 BaselineSimulator 클래스 생성
    - `src/simulation/baseline_simulator.py` 파일 생성
    - `BaselineSimulator` 클래스 구현 (baseline_manager 의존성)
    - 임계값 설정: min_baseline=1.0kg, max_baseline=5.0kg, refill_threshold=1.5kg, cleaning_threshold=4.5kg
    - _요구사항: 3.5_
  
  - [~] 6.2 이벤트 유형별 기준선 효과 구현
    - `apply_urination_effect()`: 50-100g 증가 (모래 응고)
    - `apply_defecation_effect()`: 100-200g 감소 (배설물 제거)
    - `apply_cleaning_effect()`: 200-400g 감소 (덩어리 제거)
    - `apply_refill_effect()`: 500-1000g 증가 (모래 보충)
    - _요구사항: 3.1, 3.2, 3.3, 3.4_
  
  - [~] 6.3 자동 유지보수 및 범위 검증 구현
    - `check_auto_maintenance()`: 임계값 기반 자동 이벤트 스케줄링
    - 1.5kg 이하: 24시간 내 보충 스케줄
    - 4.5kg 이상: 12시간 내 청소 스케줄
    - `ensure_valid_range()`: 1.0-5.0kg 범위 강제
    - _요구사항: 3.5, 3.6, 3.7_

- [ ] 7. LongTermSimulator 컴포넌트 구현
  - [~] 7.1 LongTermSimulator 클래스 생성
    - `src/simulation/long_term_simulator.py` 파일 생성
    - `LongTermSimulator` 클래스 구현 (database, baseline_simulator, simulation_generator 의존성)
    - 구성 검증: `validate_config()` 메서드
    - _요구사항: 4.1, 9.7_
  
  - [~] 7.2 시나리오 패턴 로직 구현
    - `apply_scenario_pattern()` 메서드 구현
    - 정상 패턴: 하루 2-4회 방문, 30-120초
    - 다뇨 발병: 3일간 정상, 이후 하루 6-10회, 15-45초
    - 점진적 체중 감소: 하루 0.5-1.0% 감소
    - 복합: 다뇨 + 체중 감소 동시 적용
    - _요구사항: 4.4, 4.5, 4.6, 4.7_
  
  - [~] 7.3 이벤트 시간 분배 구현
    - `distribute_events_in_day()` 메서드 구현
    - 현실적인 시간대에 이벤트 분배 (23:00-06:00 제외)
    - 아침/저녁 시간대에 더 많은 방문 분배
    - _요구사항: 4.8, 9.6_
  
  - [~] 7.4 단일 고양이 이벤트 생성 구현
    - `generate_events_for_cat()` 메서드 구현
    - 지정된 기간 동안 고양이별 이벤트 생성
    - 시나리오 패턴 적용
    - 기준선 변동 규칙 적용
    - 데이터 소스를 SIMULATION으로 태그
    - _요구사항: 4.2, 4.9, 4.10_
  
  - [~] 7.5 다중 고양이 시뮬레이션 구현
    - `run_simulation()` 메서드 구현 (전체 시뮬레이션 조율)
    - 여러 고양이의 이벤트 생성
    - 고양이 간 이벤트 시간 겹침 방지
    - 진행 상황 업데이트 제공
    - SimulationResult 반환
    - _요구사항: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [~] 7.6 시뮬레이션 데이터 검증 구현
    - 이벤트 지속시간 검증: 10-300초
    - 체중 검증: 프로필 체중의 ±20% 이내 (체중 감소 시나리오 제외)
    - 방문 빈도 검증: 하루 최대 15회
    - 고양이별 연속 방문 간 최소 2시간 간격
    - _요구사항: 9.1, 9.2, 9.3, 9.4, 9.5_

- [~] 8. 체크포인트 - 시뮬레이션 기능 테스트
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의하세요.

- [ ] 9. 메인 처리 파이프라인에 추적 통합
  - [~] 9.1 이벤트 처리 후 체중 추적 추가
    - `app.py`의 이벤트 처리 흐름 수정
    - 고양이 방문 이벤트 식별 후 `WeightTracker.record_measurement()` 호출
    - 체중 측정 후 `AlertGenerator.check_weight_change_alerts()` 호출
    - _요구사항: 1.1, 2.1_
  
  - [~] 9.2 기준선 변경 히스토리 로깅 추가
    - `src/preprocessing/baseline.py`의 `BaselineManager` 수정
    - 기준선 업데이트 시 `BaselineHistory` 레코드 생성
    - 이전 무게, 새 무게, 변경량, 이유 저장
    - _요구사항: 8.1, 8.2_

- [ ] 10. 체중 히스토리 시각화 UI 구현
  - [~] 10.1 체중 추적 페이지 생성
    - `app.py`에 새 페이지 "체중 추적" 추가
    - 고양이 선택기 (다중 선택 드롭다운)
    - 날짜 범위 선택기 (7일/30일/90일/전체)
    - _요구사항: 7.1, 7.5, 7.6_
  
  - [~] 10.2 체중 차트 구현
    - Plotly 또는 Altair를 사용한 라인 차트
    - 시간에 따른 측정 체중 표시
    - 프로필 체중 참조선 표시
    - 알림 마커 표시 (⚠️ 경고, 🚨 위험)
    - 고양이별 다른 색상 사용
    - _요구사항: 7.1, 7.2, 7.3, 7.7_
  
  - [~] 10.3 체중 데이터 테이블 및 내보내기
    - 차트 아래 데이터 테이블 추가
    - 열: 날짜, 고양이, 측정 체중, 프로필 체중, 차이, 변화율
    - 정렬 및 필터링 지원
    - CSV 내보내기 버튼
    - _요구사항: 7.4_

- [ ] 11. 장기 시뮬레이션 구성 UI 구현
  - [~] 11.1 시뮬레이션 구성 페이지 생성
    - `app.py`에 새 페이지 "장기 시뮬레이션" 추가
    - 기간 선택기 (7/14/30일)
    - 시작 날짜/시간 선택기
    - _요구사항: 6.1, 6.4_
  
  - [~] 11.2 고양이별 시나리오 구성 UI
    - 고양이 구성 테이블
    - 열: 고양이 이름, 시나리오, 포함 (체크박스)
    - 고양이별 시나리오 드롭다운 (정상/다뇨 발병/체중 감소/복합)
    - _요구사항: 6.2, 6.3_
  
  - [~] 11.3 시뮬레이션 미리보기 및 실행
    - 미리보기 섹션: 예상 이벤트, 예상 알림, 예상 실행 시간
    - "시뮬레이션 실행" 버튼
    - 진행률 표시줄 (실행 중)
    - 결과 요약 (완료 후): 생성된 이벤트, 생성된 알림, 고양이별 체중 변화
    - _요구사항: 6.5, 6.6, 6.7, 6.8_

- [ ] 12. 기준선 히스토리 타임라인 UI 구현
  - [~] 12.1 기준선 히스토리 페이지 생성
    - `app.py`에 새 섹션 또는 페이지 "기준선 히스토리" 추가
    - 타임라인 시각화 (단계 차트)
    - 이벤트 유형별 색상 구분 마커
    - _요구사항: 8.3, 8.4_
  
  - [~] 12.2 기준선 통계 및 필터
    - 통계 패널: 평균 기준선 (24시간/7일/30일), 총 보충, 총 청소
    - 필터 컨트롤: 날짜 범위, 이벤트 유형, 데이터 소스
    - _요구사항: 8.5_

- [ ] 13. 데이터 소스 제어 패널 UI 구현
  - [~] 13.1 데이터 소스 모드 전환 UI
    - 사이드바 또는 설정 페이지에 모드 선택기 추가
    - 라디오 버튼: "시뮬레이션" / "센서"
    - 현재 모드 표시 (📊 시뮬레이션 모드 / 📡 센서 모드)
    - _요구사항: 11.8, 11.9_
  
  - [~] 13.2 센서 연결 상태 표시
    - 연결 상태 표시기 (🟢 연결됨 / 🟡 연결 끊김 / 🔴 오류)
    - 마지막 수신 데이터 타임스탬프
    - 장치 ID 표시
    - 재연결 버튼
    - _요구사항: 11.7, 11.12_

- [ ] 14. 대시보드 개선 및 알림 표시
  - [~] 14.1 홈 대시보드에 데이터 소스 표시기 추가
    - 상단 우측에 현재 데이터 소스 표시
    - 센서 모드일 때 연결 상태 표시
    - _요구사항: 11.9_
  
  - [~] 14.2 고양이별 체중 추세 표시기 추가
    - 각 고양이에 대한 추세 표시기 (↗️ 증가 / → 안정 / ↘️ 감소)
    - 최근 7일 간단한 체중 차트
    - _요구사항: 7.1_
  
  - [~] 14.3 알림 요약 섹션 추가
    - 심각도별 알림 개수 표시
    - 최근 알림 목록 (확장 가능)
    - _요구사항: 2.4_

- [ ] 15. 시뮬레이션 데이터 정리 기능 구현
  - [~] 15.1 이벤트 삭제 UI 추가
    - 설정 페이지에 "데이터 정리" 섹션 추가
    - 날짜 범위 선택기
    - 데이터 소스 필터 (시뮬레이션/실제 센서)
    - 삭제 확인 대화상자 (삭제될 이벤트 수 표시)
    - _요구사항: 10.1, 10.2, 10.3_
  
  - [~] 15.2 삭제 로직 구현
    - `src/storage/database.py`에 `delete_events()` 메서드 추가
    - 관련 체중 측정 및 알림도 삭제
    - 고양이 프로필은 보존
    - 삭제 요약 표시
    - _요구사항: 10.4, 10.5, 10.6_
  
  - [~] 15.3 기준선 재설정 옵션 추가
    - 시뮬레이션 데이터 삭제 후 기준선 재설정 옵션
    - 사용자 지정 값으로 기준선 설정
    - _요구사항: 10.7_

- [~] 16. 최종 체크포인트 - 통합 테스트 및 검증
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의하세요.

## 참고사항

- 모든 구현은 Python으로 작성됩니다
- 기존 아키텍처와의 호환성을 유지합니다
- 시뮬레이션과 실제 센서 데이터는 동일한 처리 파이프라인을 사용합니다
- UI는 Streamlit을 사용하여 구현됩니다
- 모든 데이터는 JSON 파일로 저장됩니다 (개발 단계)
- 체중 변화 알림은 중복 방지 로직을 포함합니다
- 장기 시뮬레이션은 현실적인 시간 분배를 사용합니다
- 기준선 변동은 자동 유지보수 이벤트를 트리거합니다

## 작업 의존성 그래프

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "1.4", "1.5"] },
    { "id": 1, "tasks": ["1.6", "2.1", "3.1", "5.1", "6.1", "7.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.2", "5.2", "5.3", "6.2", "7.2"] },
    { "id": 3, "tasks": ["3.3", "5.4", "6.3", "7.3", "7.4"] },
    { "id": 4, "tasks": ["7.5", "7.6", "9.1", "9.2"] },
    { "id": 5, "tasks": ["10.1", "11.1", "12.1", "13.1"] },
    { "id": 6, "tasks": ["10.2", "10.3", "11.2", "11.3", "12.2", "13.2"] },
    { "id": 7, "tasks": ["14.1", "14.2", "14.3", "15.1"] },
    { "id": 8, "tasks": ["15.2", "15.3"] }
  ]
}
```
