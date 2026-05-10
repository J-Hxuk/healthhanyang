"""
Sensor Data Receiver Module

Receives and processes ESP32 JSON payloads
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging

from .schema import RawSensorData
from .validator import PayloadValidator, ValidationResult


logger = logging.getLogger(__name__)


class SensorDataReceiver:
    """Receives and validates ESP32 sensor data"""
    
    def __init__(self):
        self.validator = PayloadValidator()
    
    def parse_payload(self, json_str: str) -> Optional[Dict]:
        """
        Parse JSON string to dictionary
        
        Args:
            json_str: JSON string from ESP32
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        try:
            payload = json.loads(json_str)
            return payload
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Invalid JSON: {json_str[:200]}")  # Log first 200 chars
            return None
    
    def validate_payload(self, payload: Dict) -> ValidationResult:
        """
        Validate payload structure and data
        
        Args:
            payload: Parsed payload dictionary
            
        Returns:
            ValidationResult with validation status
        """
        return self.validator.validate(payload)
    
    def save_raw_data(self, payload: Dict) -> RawSensorData:
        """
        Create RawSensorData object from validated payload
        
        Args:
            payload: Validated payload dictionary
            
        Returns:
            RawSensorData object with received_at timestamp
        """
        # Generate unique ID
        data_id = str(uuid.uuid4())
        
        # Record received timestamp
        received_at = datetime.now()
        
        # Create RawSensorData object
        raw_data = RawSensorData(
            id=data_id,
            device_id=payload['device_id'],
            timestamp=payload['timestamp'],
            received_at=received_at,
            loadcell_1=float(payload['loadcell_1']),
            loadcell_2=float(payload['loadcell_2']),
            loadcell_3=float(payload['loadcell_3']),
            loadcell_4=float(payload['loadcell_4']),
            total_weight=float(payload['total_weight'])
        )
        
        return raw_data
    
    def receive(self, json_str: str) -> Optional[RawSensorData]:
        """
        Complete receive pipeline: parse, validate, and create RawSensorData
        
        Args:
            json_str: JSON string from ESP32
            
        Returns:
            RawSensorData object if successful, None if validation fails
        """
        # Parse JSON
        payload = self.parse_payload(json_str)
        if payload is None:
            return None
        
        # Validate payload
        validation_result = self.validate_payload(payload)
        if not validation_result.is_valid:
            logger.warning(f"Payload validation failed: {validation_result.errors}")
            return None
        
        # Create RawSensorData
        raw_data = self.save_raw_data(payload)
        logger.info(f"Received sensor data: device={raw_data.device_id}, weight={raw_data.total_weight:.3f}kg")
        
        return raw_data
