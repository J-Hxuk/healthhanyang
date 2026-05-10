"""
Payload Validation Module

Validates ESP32 JSON payloads for required fields and data integrity
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class ValidationResult:
    """Result of payload validation"""
    is_valid: bool
    errors: List[str]
    
    def __bool__(self) -> bool:
        return self.is_valid


class PayloadValidator:
    """Validates ESP32 sensor data payloads"""
    
    REQUIRED_FIELDS = [
        'device_id',
        'timestamp',
        'loadcell_1',
        'loadcell_2',
        'loadcell_3',
        'loadcell_4',
        'total_weight'
    ]
    
    MAX_REASONABLE_WEIGHT = 50.0  # kg - maximum reasonable weight for litter box
    
    def validate(self, payload: Dict) -> ValidationResult:
        """
        Validate ESP32 JSON payload
        
        Args:
            payload: Dictionary containing sensor data
            
        Returns:
            ValidationResult with validation status and error messages
        """
        errors = []
        
        # Check required fields
        missing_fields = self._check_required_fields(payload)
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Validate numeric fields
        numeric_errors = self._validate_numeric_fields(payload)
        errors.extend(numeric_errors)
        
        # Validate weight values
        weight_errors = self._validate_weights(payload)
        errors.extend(weight_errors)
        
        # Validate total_weight consistency
        consistency_errors = self._validate_total_weight_consistency(payload)
        errors.extend(consistency_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors)
    
    def _check_required_fields(self, payload: Dict) -> List[str]:
        """Check for missing required fields"""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in payload:
                missing.append(field)
        return missing
    
    def _validate_numeric_fields(self, payload: Dict) -> List[str]:
        """Validate that numeric fields contain valid numbers"""
        errors = []
        
        numeric_fields = [
            'timestamp',
            'loadcell_1',
            'loadcell_2',
            'loadcell_3',
            'loadcell_4',
            'total_weight'
        ]
        
        for field in numeric_fields:
            value = payload.get(field)
            
            # Check if value is numeric
            if not isinstance(value, (int, float)):
                errors.append(f"{field} must be numeric, got {type(value).__name__}")
                continue
            
            # Check for NaN
            if isinstance(value, float) and math.isnan(value):
                errors.append(f"{field} contains NaN")
            
            # Check for infinity
            if isinstance(value, float) and math.isinf(value):
                errors.append(f"{field} contains infinity")
        
        return errors
    
    def _validate_weights(self, payload: Dict) -> List[str]:
        """Validate weight values are reasonable"""
        errors = []
        
        weight_fields = [
            'loadcell_1',
            'loadcell_2',
            'loadcell_3',
            'loadcell_4',
            'total_weight'
        ]
        
        for field in weight_fields:
            value = payload.get(field)
            
            if not isinstance(value, (int, float)):
                continue  # Already caught by numeric validation
            
            # Check for negative weights
            if value < 0:
                errors.append(f"{field} cannot be negative: {value}")
            
            # Check for unreasonably large weights
            if value > self.MAX_REASONABLE_WEIGHT:
                errors.append(f"{field} exceeds maximum reasonable weight ({self.MAX_REASONABLE_WEIGHT} kg): {value}")
        
        return errors
    
    def _validate_total_weight_consistency(self, payload: Dict) -> List[str]:
        """Validate that total_weight approximately equals sum of load cells"""
        errors = []
        
        try:
            loadcell_sum = (
                payload['loadcell_1'] +
                payload['loadcell_2'] +
                payload['loadcell_3'] +
                payload['loadcell_4']
            )
            total_weight = payload['total_weight']
            
            # Allow 5% tolerance for rounding errors
            tolerance = 0.05 * max(abs(loadcell_sum), abs(total_weight))
            tolerance = max(tolerance, 0.01)  # Minimum 10g tolerance
            
            difference = abs(total_weight - loadcell_sum)
            
            if difference > tolerance:
                errors.append(
                    f"total_weight ({total_weight}) does not match sum of load cells "
                    f"({loadcell_sum:.3f}), difference: {difference:.3f} kg"
                )
        
        except (KeyError, TypeError):
            # Fields missing or not numeric - already caught by other validations
            pass
        
        return errors
