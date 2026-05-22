"""
Event Detection Module

Detects events from weight changes and extracts features
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass
import statistics
import logging

from ..data.schema import ProcessedSensorData, Event, EventType, DataSourceMode
from config.config import get_config


logger = logging.getLogger(__name__)


@dataclass
class OngoingEvent:
    """Tracks an event in progress"""
    event_id: str
    device_id: str
    start_time: datetime
    baseline_before: float
    weights: List[float]
    timestamps: List[datetime]


class EventDetector:
    """Detects events from weight changes"""
    
    def __init__(self, device_id: str, data_source: DataSourceMode = DataSourceMode.SIMULATION):
        """
        Initialize event detector
        
        Args:
            device_id: Device ID for this detector
            data_source: Data source mode (SIMULATION or SENSOR)
        """
        self.device_id = device_id
        self.config = get_config()
        self.current_event: Optional[OngoingEvent] = None
        self.current_baseline: Optional[float] = None
        self.data_source = data_source
    
    def update_baseline(self, baseline: float):
        """Update current baseline weight"""
        self.current_baseline = baseline
    
    def detect_start(self, weight: float, baseline: float) -> bool:
        """
        Check if event should start
        
        Args:
            weight: Current weight
            baseline: Current baseline weight
            
        Returns:
            True if event should start
        """
        if baseline is None:
            logger.debug("Cannot detect start: baseline is None")
            return False
        
        threshold = self.config.weight_change_threshold
        should_start = weight > baseline + threshold
        
        if should_start:
            logger.info(f"Event start detected: weight={weight:.3f}kg > baseline={baseline:.3f}kg + threshold={threshold:.3f}kg")
        
        return should_start
    
    def detect_end(self, weight: float, baseline: float) -> bool:
        """
        Check if ongoing event should end
        
        Args:
            weight: Current weight
            baseline: Current baseline weight
            
        Returns:
            True if event should end
        """
        if baseline is None:
            logger.debug("Cannot detect end: baseline is None")
            return False
        
        threshold = self.config.weight_change_threshold
        # Event ends when weight returns close to baseline
        should_end = abs(weight - baseline) < threshold
        
        if should_end:
            logger.info(f"Event end detected: weight={weight:.3f}kg close to baseline={baseline:.3f}kg (diff={abs(weight - baseline):.3f}kg < threshold={threshold:.3f}kg)")
        
        return should_end
    
    def process(self, processed_data: ProcessedSensorData, baseline: float) -> Optional[Event]:
        """
        Process weight measurement and detect events
        
        Args:
            processed_data: Processed sensor data
            baseline: Current baseline weight
            
        Returns:
            Completed Event if event ended, None otherwise
        """
        weight = processed_data.filtered_weight
        timestamp = processed_data.processing_timestamp
        
        # Update baseline
        self.current_baseline = baseline
        
        # Check for event timeout
        if self.current_event is not None:
            duration = (timestamp - self.current_event.start_time).total_seconds()
            if duration > self.config.max_event_duration:
                logger.warning(f"Event timeout after {duration:.1f}s, force-closing")
                event = self._finalize_event(baseline, EventType.UNKNOWN)
                self.current_event = None
                return event
        
        # State machine: no event vs ongoing event
        if self.current_event is None:
            # No ongoing event - check for start
            if self.detect_start(weight, baseline):
                self._start_event(weight, timestamp, baseline)
                logger.info(f"Event started: weight={weight:.3f}kg, baseline={baseline:.3f}kg")
        
        else:
            # Ongoing event - track weight and check for end
            self.current_event.weights.append(weight)
            self.current_event.timestamps.append(timestamp)
            
            duration = (timestamp - self.current_event.start_time).total_seconds()
            logger.debug(f"Event ongoing: duration={duration:.1f}s, weight={weight:.3f}kg, baseline={baseline:.3f}kg")
            
            if self.detect_end(weight, baseline):
                # Check minimum duration
                if duration >= self.config.min_event_duration:
                    logger.info(f"Event ended: duration={duration:.1f}s, meets minimum={self.config.min_event_duration}s")
                    event = self._finalize_event(baseline, None)
                    self.current_event = None
                    return event
                else:
                    logger.debug(f"Event too short ({duration:.1f}s < {self.config.min_event_duration}s), continuing")
        
        return None
    
    def has_ongoing_event(self) -> bool:
        """Check if there is an ongoing event"""
        return self.current_event is not None
    
    def has_ongoing_event(self) -> bool:
        """Check if there is an ongoing event"""
        return self.current_event is not None
    
    def _start_event(self, weight: float, timestamp: datetime, baseline: float):
        """Start tracking a new event"""
        self.current_event = OngoingEvent(
            event_id=str(uuid.uuid4()),
            device_id=self.device_id,
            start_time=timestamp,
            baseline_before=baseline,
            weights=[weight],
            timestamps=[timestamp]
        )
    
    def _finalize_event(self, baseline_after: float, forced_type: Optional[EventType]) -> Event:
        """
        Finalize ongoing event and extract features
        
        Args:
            baseline_after: Baseline weight after event
            forced_type: Force event type (e.g., UNKNOWN for timeout)
            
        Returns:
            Completed Event object
        """
        if self.current_event is None:
            raise ValueError("No ongoing event to finalize")
        
        # Calculate features
        duration = (self.current_event.timestamps[-1] - self.current_event.start_time).total_seconds()
        max_weight = max(self.current_event.weights)
        avg_weight = statistics.mean(self.current_event.weights)
        weight_gain = max_weight - self.current_event.baseline_before
        baseline_shift = abs(baseline_after - self.current_event.baseline_before)
        
        # Calculate stability score (inverse of variance, normalized to 0-1)
        if len(self.current_event.weights) > 1:
            variance = statistics.variance(self.current_event.weights)
            # Normalize: high variance = low stability
            # Use exponential decay: stability = exp(-variance)
            import math
            stability_score = math.exp(-variance * 10)  # Scale factor for sensitivity
            stability_score = max(0.0, min(1.0, stability_score))
        else:
            stability_score = 1.0
        
        # Create Event object (classification will be done separately)
        event = Event(
            event_id=self.current_event.event_id,
            device_id=self.device_id,
            cat_id=None,  # Will be filled by identifier
            event_type=forced_type if forced_type else EventType.UNKNOWN,  # Will be classified
            start_time=self.current_event.start_time,
            end_time=self.current_event.timestamps[-1],
            duration=duration,
            baseline_before=self.current_event.baseline_before,
            baseline_after=baseline_after,
            max_weight=max_weight,
            avg_weight=avg_weight,
            weight_gain=weight_gain,
            baseline_shift=baseline_shift,
            stability_score=stability_score,
            confidence_score=0.0,  # Will be filled by classifier
            data_source=self.data_source
        )
        
        logger.debug(f"Event finalized: duration={duration:.1f}s, weight_gain={weight_gain:.3f}kg, stability={stability_score:.2f}")
        
        return event
