"""
Baseline Weight Management Module

Maintains accurate baseline weight (empty litter box + litter)
"""

import uuid
from datetime import datetime
from typing import List, Optional
from collections import deque
import statistics
import logging

from ..data.schema import ProcessedSensorData, BaselineHistory, DataSourceMode
from config.config import get_config


logger = logging.getLogger(__name__)


class BaselineManager:
    """Manages baseline weight calculation and updates"""
    
    def __init__(self, device_id: str, database=None, data_source: DataSourceMode = DataSourceMode.SIMULATION):
        """
        Initialize baseline manager
        
        Args:
            device_id: Device ID for this baseline manager
            database: Optional Database instance for persisting history
            data_source: Data source mode (SIMULATION or SENSOR)
        """
        self.device_id = device_id
        self.config = get_config()
        self.current_baseline: Optional[float] = None
        self.history: List[BaselineHistory] = []
        self.stability_window = deque(maxlen=20)  # Track recent weights for stability
        self.database = database
        self.data_source = data_source
    
    def calculate_baseline(self, stable_weights: List[float]) -> float:
        """
        Calculate baseline from stable weight sequence
        
        Args:
            stable_weights: List of stable weight measurements
            
        Returns:
            Calculated baseline weight
        """
        if not stable_weights:
            raise ValueError("Cannot calculate baseline from empty weight list")
        
        # Use median for robustness against outliers
        baseline = statistics.median(stable_weights)
        
        logger.debug(f"Calculated baseline: {baseline:.3f}kg from {len(stable_weights)} samples")
        
        return baseline
    
    def is_stable(self, weights: List[float], duration: Optional[float] = None) -> bool:
        """
        Check if weight sequence is stable
        
        Args:
            weights: List of recent weight measurements
            duration: Minimum duration in seconds (not used in this simplified version)
            
        Returns:
            True if weights are stable, False otherwise
        """
        if len(weights) < 5:
            # Need at least 5 samples to determine stability
            return False
        
        try:
            # Calculate variance
            variance = statistics.variance(weights)
            
            # Stable if variance is very low
            # Using noise_threshold as stability criterion
            stability_threshold = self.config.noise_threshold ** 2
            
            is_stable = variance < stability_threshold
            
            logger.debug(f"Stability check: variance={variance:.6f}, threshold={stability_threshold:.6f}, stable={is_stable}")
            
            return is_stable
        
        except statistics.StatisticsError:
            return False
    
    def update_baseline(self, new_baseline: float, reason: str):
        """
        Update baseline weight with timestamp and reason
        
        Args:
            new_baseline: New baseline weight value
            reason: Reason for update (stable, cleaning, litter_refill, user_reset)
        """
        previous_weight = self.current_baseline if self.current_baseline is not None else new_baseline
        change_amount = new_baseline - previous_weight
        
        self.current_baseline = new_baseline
        
        # Create history record with new fields
        history_record = BaselineHistory(
            id=str(uuid.uuid4()),
            device_id=self.device_id,
            baseline_weight=new_baseline,
            timestamp=datetime.now(),
            reason=reason,
            previous_weight=previous_weight,
            change_amount=change_amount,
            data_source=self.data_source
        )
        
        self.history.append(history_record)
        
        # Save to database if available
        if self.database:
            self.database.save_baseline_history(history_record)
        
        logger.info(f"Baseline updated: {previous_weight:.3f} -> {new_baseline:.3f}kg "
                   f"(change: {change_amount:+.3f}kg, reason: {reason})")
    
    def get_current_baseline(self) -> Optional[float]:
        """Get current baseline weight"""
        return self.current_baseline
    
    def reset_baseline(self):
        """User-triggered baseline recalibration"""
        if len(self.stability_window) >= 5:
            stable_weights = list(self.stability_window)
            new_baseline = self.calculate_baseline(stable_weights)
            self.update_baseline(new_baseline, "user_reset")
        else:
            logger.warning("Not enough data for baseline reset. Need at least 5 stable readings.")
    
    def process_weight(self, processed_data: ProcessedSensorData, event_in_progress: bool = False) -> Optional[float]:
        """
        Process weight measurement and update baseline if stable
        
        Args:
            processed_data: Processed sensor data
            event_in_progress: If True, don't update baseline (event is ongoing)
            
        Returns:
            Current baseline weight (may be updated)
        """
        weight = processed_data.filtered_weight
        
        # Add to stability window
        self.stability_window.append(weight)
        
        # If no baseline yet, try to establish one
        if self.current_baseline is None:
            if self.is_stable(list(self.stability_window)):
                initial_baseline = self.calculate_baseline(list(self.stability_window))
                self.update_baseline(initial_baseline, "stable")
        
        # Don't update baseline during an event
        elif not event_in_progress:
            # Check if we should update baseline (weight has been stable)
            if self.is_stable(list(self.stability_window)):
                stable_weights = list(self.stability_window)
                potential_baseline = self.calculate_baseline(stable_weights)
                
                # Only update if change is significant (more than noise threshold)
                if abs(potential_baseline - self.current_baseline) > self.config.noise_threshold:
                    # Check if this looks like a baseline shift (not a cat on pad)
                    # If weight is much higher than current baseline, it's likely a cat, not a baseline change
                    if potential_baseline < self.current_baseline + self.config.cat_min_weight:
                        self.update_baseline(potential_baseline, "stable")
        
        return self.current_baseline
    
    def force_update_after_event(self, new_baseline: float, event_type: str):
        """
        Force baseline update after cleaning or litter refill event
        
        Args:
            new_baseline: New baseline weight
            event_type: Type of event (cleaning or litter_refill)
        """
        self.update_baseline(new_baseline, event_type)
        # Clear stability window to start fresh
        self.stability_window.clear()
    
    def get_baseline_history(self, limit: Optional[int] = None) -> List[BaselineHistory]:
        """
        Get baseline history records
        
        Args:
            limit: Maximum number of records to return (most recent first)
            
        Returns:
            List of BaselineHistory records
        """
        if limit is None:
            return list(reversed(self.history))
        else:
            return list(reversed(self.history[-limit:]))
