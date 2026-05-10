"""
Sensor Preprocessing Module

Applies noise filtering and moving average to stabilize weight measurements
"""

import uuid
from datetime import datetime
from typing import List, Optional
from collections import deque
import statistics
import logging

from ..data.schema import RawSensorData, ProcessedSensorData
from config.config import get_config


logger = logging.getLogger(__name__)


class SensorPreprocessor:
    """Preprocesses raw sensor data to reduce noise and stabilize measurements"""
    
    def __init__(self, window_size: Optional[int] = None):
        """
        Initialize preprocessor
        
        Args:
            window_size: Size of moving average window. If None, uses config value.
        """
        self.config = get_config()
        self.window_size = window_size if window_size is not None else self.config.moving_average_window
        self.weight_window = deque(maxlen=self.window_size)
        self.previous_filtered = None
    
    def apply_moving_average(self, weights: List[float]) -> float:
        """
        Calculate moving average of weight values
        
        Args:
            weights: List of recent weight values
            
        Returns:
            Moving average value
        """
        if not weights:
            return 0.0
        
        return statistics.mean(weights)
    
    def filter_noise(self, current: float, previous: Optional[float], threshold: Optional[float] = None) -> float:
        """
        Suppress small weight changes below noise threshold
        
        Args:
            current: Current weight value
            previous: Previous filtered weight value
            threshold: Noise threshold in kg. If None, uses config value.
            
        Returns:
            Filtered weight (either current or previous based on threshold)
        """
        if previous is None:
            return current
        
        if threshold is None:
            threshold = self.config.noise_threshold
        
        difference = abs(current - previous)
        
        if difference < threshold:
            # Change is below threshold, suppress it
            return previous
        else:
            # Change is significant, accept it
            return current
    
    def detect_outlier(self, value: float, history: List[float], threshold: Optional[float] = None) -> bool:
        """
        Detect if value is an outlier based on standard deviation
        
        Args:
            value: Value to check
            history: Recent historical values
            threshold: Number of standard deviations for outlier detection. If None, uses config.
            
        Returns:
            True if value is an outlier, False otherwise
        """
        if len(history) < 3:
            # Not enough history to determine outliers
            return False
        
        if threshold is None:
            threshold = self.config.outlier_threshold
        
        try:
            mean = statistics.mean(history)
            stdev = statistics.stdev(history)
            
            if stdev == 0:
                # No variation in history
                return abs(value - mean) > self.config.noise_threshold
            
            z_score = abs(value - mean) / stdev
            
            return z_score > threshold
        
        except statistics.StatisticsError:
            # Not enough data or other statistical error
            return False
    
    def process(self, raw_data: RawSensorData) -> ProcessedSensorData:
        """
        Apply all preprocessing filters to raw sensor data
        
        Args:
            raw_data: Raw sensor data from ESP32
            
        Returns:
            ProcessedSensorData with filtered weight
        """
        current_weight = raw_data.total_weight
        
        # Add to sliding window
        self.weight_window.append(current_weight)
        
        # Step 1: Apply moving average
        avg_weight = self.apply_moving_average(list(self.weight_window))
        
        # Step 2: Check for outliers
        if len(self.weight_window) >= 3:
            history = list(self.weight_window)[:-1]  # Exclude current value
            is_outlier = self.detect_outlier(current_weight, history)
            
            if is_outlier:
                logger.warning(f"Outlier detected: {current_weight:.3f}kg (history mean: {statistics.mean(history):.3f}kg)")
                # Use moving average of history instead of current value
                filtered_weight = statistics.mean(history)
            else:
                filtered_weight = avg_weight
        else:
            filtered_weight = avg_weight
        
        # Step 3: Apply noise filtering
        filtered_weight = self.filter_noise(filtered_weight, self.previous_filtered)
        
        # Update previous filtered value
        self.previous_filtered = filtered_weight
        
        # Create ProcessedSensorData
        processed_data = ProcessedSensorData(
            id=str(uuid.uuid4()),
            raw_id=raw_data.id,
            filtered_weight=filtered_weight,
            processing_timestamp=datetime.now()
        )
        
        logger.debug(f"Processed: raw={current_weight:.3f}kg, filtered={filtered_weight:.3f}kg")
        
        return processed_data
    
    def reset(self):
        """Reset preprocessor state (clear window and previous value)"""
        self.weight_window.clear()
        self.previous_filtered = None
        logger.info("Preprocessor state reset")
