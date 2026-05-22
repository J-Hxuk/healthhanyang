"""
Flask Server for ESP32 Sensor Data

Receives data from ESP32 and processes it through the pipeline
"""

from flask import Flask, request, jsonify
import logging
from datetime import datetime

from src.data.esp32_adapter import ESP32DataAdapter
from src.data.receiver import SensorDataReceiver
from src.storage.database import Database
from src.preprocessing.filter import NoiseFilter
from src.preprocessing.baseline import BaselineManager
from src.events.detector import EventDetector
from src.events.classifier import EventClassifier
from src.identification.cat_identifier import CatIdentifier
from src.tracking.weight_tracker import WeightTracker
from src.alerts.alert_generator import AlertGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)

# 컴포넌트 초기화
database = Database()
esp32_adapter = ESP32DataAdapter(device_id="esp32_001", calibration_factor=1.0)
receiver = SensorDataReceiver()
noise_filter = NoiseFilter()
baseline_manager = BaselineManager(database=database, data_source='sensor')
event_detector = EventDetector()
event_classifier = EventClassifier()
cat_identifier = CatIdentifier()
weight_tracker = WeightTracker(database=database)
alert_generator = AlertGenerator(database=database)

logger.info("Flask server initialized with all components")


@app.route('/data', methods=['POST'])
def receive_data():
    """
    ESP32 센서 데이터 수신 엔드포인트
    
    Expected format from ESP32:
    {
        "loadcell1": 12345,
        "loadcell2": 23456,
        "loadcell3": 34567,
        "loadcell4": 45678,
        "total": 115746
    }
    """
    try:
        # ESP32에서 JSON 데이터 받기
        esp32_data = request.get_json()
        
        if not esp32_data:
            logger.warning("Empty payload received")
            return jsonify({"status": "error", "message": "Empty payload"}), 400
        
        logger.info(f"Received ESP32 data: {esp32_data}")
        
        # ESP32 형식을 시스템 형식으로 변환
        standardized_data = esp32_adapter.adapt(esp32_data)
        
        if not standardized_data:
            logger.error("Failed to adapt ESP32 data")
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
        
        # 데이터 수신 및 검증
        import json
        raw_data = receiver.receive(json.dumps(standardized_data))
        
        if not raw_data:
            logger.error("Data validation failed")
            return jsonify({"status": "error", "message": "Validation failed"}), 400
        
        # 데이터베이스에 저장
        database.save_raw_data(raw_data)
        logger.info(f"Saved raw data: {raw_data.id}")
        
        # 노이즈 필터링
        filtered_data = noise_filter.filter(raw_data)
        database.save_processed_data(filtered_data)
        
        # 기준선 업데이트
        baseline_manager.update_baseline(filtered_data.total_weight)
        current_baseline = baseline_manager.get_current_baseline()
        
        # 이벤트 감지
        if current_baseline:
            event = event_detector.detect(filtered_data, current_baseline)
            
            if event:
                # 이벤트 분류
                classified_event = event_classifier.classify(event)
                
                # 고양이 식별
                identified_event = cat_identifier.identify(classified_event)
                
                # 이벤트 저장
                database.save_event(identified_event)
                logger.info(f"Event detected and saved: {identified_event.event_type}")
                
                # 체중 추적 (입실 이벤트인 경우)
                if identified_event.event_type == 'entry':
                    weight_tracker.record_measurement(identified_event)
                    
                    # 체중 변화 알림 확인
                    if identified_event.cat_id:
                        change_rate = weight_tracker.calculate_weight_change_rate(
                            identified_event.cat_id,
                            days=7
                        )
                        
                        if change_rate is not None:
                            alert = alert_generator.check_weight_change(
                                identified_event.cat_id,
                                change_rate,
                                days=7
                            )
                            
                            if alert:
                                logger.warning(f"Weight alert generated: {alert.severity} - {alert.message}")
        
        return jsonify({
            "status": "success",
            "message": "Data processed successfully",
            "data_id": raw_data.id,
            "total_weight": raw_data.total_weight,
            "baseline": current_baseline.weight if current_baseline else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/calibrate', methods=['POST'])
def calibrate():
    """
    로드셀 보정 엔드포인트
    
    Expected format:
    {
        "raw_value": 12345,
        "known_weight_kg": 5.0
    }
    """
    try:
        data = request.get_json()
        
        raw_value = data.get('raw_value')
        known_weight = data.get('known_weight_kg')
        
        if raw_value is None or known_weight is None:
            return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
        # 보정 계수 계산
        factor = esp32_adapter.calibrate(raw_value, known_weight)
        
        # 보정 계수 적용
        esp32_adapter.set_calibration_factor(factor)
        
        logger.info(f"Calibration updated: factor={factor}")
        
        return jsonify({
            "status": "success",
            "calibration_factor": factor,
            "message": f"Calibration factor set to {factor}"
        }), 200
        
    except Exception as e:
        logger.error(f"Calibration error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """서버 상태 확인"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "calibration_factor": esp32_adapter.calibration_factor,
        "device_id": esp32_adapter.device_id
    }), 200


if __name__ == '__main__':
    # Flask 서버 실행
    # ESP32 코드에서 설정한 주소: http://172.20.10.5:5000/data
    app.run(host='0.0.0.0', port=5000, debug=True)
