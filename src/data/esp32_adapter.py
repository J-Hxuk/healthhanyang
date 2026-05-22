"""
ESP32 Data Adapter Module

Converts ESP32 raw sensor data to standardized format
"""

from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ESP32DataAdapter:
    """Adapts ESP32 raw data format to system format"""
    
    def __init__(self, device_id: str = "esp32_001", calibration_factor: float = 1.0):
        """
        Initialize adapter
        
        Args:
            device_id: Device identifier for this ESP32
            calibration_factor: Conversion factor from raw values to kg (default: 1.0)
                               Will be updated after calibration
        """
        self.device_id = device_id
        self.calibration_factor = calibration_factor
    
    def adapt(self, esp32_payload: Dict) -> Optional[Dict]:
        """
        Convert ESP32 format to system format
        
        ESP32 format:
        {
            "loadcell1": 12345,
            "loadcell2": 23456,
            "loadcell3": 34567,
            "loadcell4": 45678,
            "total": 115746
        }
        
        System format:
        {
            "device_id": "esp32_001",
            "timestamp": 1234567890,
            "loadcell_1": 1.234,
            "loadcell_2": 2.345,
            "loadcell_3": 3.456,
            "loadcell_4": 4.567,
            "total_weight": 11.602
        }
        
        Args:
            esp32_payload: Raw payload from ESP32
            
        Returns:
            Standardized payload or None if conversion fails
        """
        try:
            # Extract raw values
            raw1 = esp32_payload.get('loadcell1', 0)
            raw2 = esp32_payload.get('loadcell2', 0)
            raw3 = esp32_payload.get('loadcell3', 0)
            raw4 = esp32_payload.get('loadcell4', 0)
            raw_total = esp32_payload.get('total', 0)
            
            # Apply calibration factor to convert to kg
            # For now, just use raw values as-is (calibration_factor = 1.0)
            # After calibration, update calibration_factor
            weight1 = raw1 * self.calibration_factor
            weight2 = raw2 * self.calibration_factor
            weight3 = raw3 * self.calibration_factor
            weight4 = raw4 * self.calibration_factor
            total_weight = raw_total * self.calibration_factor
            
            # Create standardized payload
            standardized = {
                'device_id': self.device_id,
                'timestamp': int(datetime.now().timestamp()),
                'loadcell_1': weight1,
                'loadcell_2': weight2,
                'loadcell_3': weight3,
                'loadcell_4': weight4,
                'total_weight': total_weight
            }
            
            logger.debug(f"Adapted ESP32 data: raw_total={raw_total} -> weight={total_weight:.3f}kg")
            return standardized
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to adapt ESP32 payload: {e}")
            logger.debug(f"Invalid payload: {esp32_payload}")
            return None
    
    def set_calibration_factor(self, factor: float):
        """
        Update calibration factor
        
        Args:
            factor: New calibration factor (raw_value * factor = kg)
        """
        if factor <= 0:
            logger.warning(f"Invalid calibration factor: {factor}. Must be positive.")
            return
        
        self.calibration_factor = factor
        logger.info(f"Calibration factor updated to {factor}")
    
    def calibrate(self, raw_value: float, known_weight_kg: float) -> float:
        """
        Calculate calibration factor from known weight
        
        Args:
            raw_value: Raw sensor reading
            known_weight_kg: Actual weight in kg
            
        Returns:
            Calculated calibration factor
        """
        if raw_value == 0:
            logger.error("Cannot calibrate with zero raw value")
            return self.calibration_factor
        
        factor = known_weight_kg / raw_value
        logger.info(f"Calculated calibration factor: {factor} (raw={raw_value}, weight={known_weight_kg}kg)")
        return factor
