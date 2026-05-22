"""
Weight Tracker Module

Tracks cat weight measurements over time and calculates trends
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from ..data.schema import Event, CatProfile, WeightMeasurement, DataSourceMode
from ..storage.database import Database


logger = logging.getLogger(__name__)


class WeightTracker:
    """Tracks cat weight measurements over time"""
    
    def __init__(self, database: Database):
        """
        Initialize weight tracker
        
        Args:
            database: Database instance for storage
        """
        self.db = database
    
    def record_measurement(self, event: Event, cat_profile: CatProfile, 
                          data_source: Optional[DataSourceMode] = None) -> WeightMeasurement:
        """
        Record weight measurement from event
        
        Args:
            event: Event with weight data
            cat_profile: Cat profile with baseline weight
            data_source: Data source mode (defaults to event's data_source)
            
        Returns:
            Created WeightMeasurement
        """
        # Calculate measured weight: event.avg_weight - event.baseline_before
        measured_weight = event.avg_weight - event.baseline_before
        
        # Calculate weight difference from profile
        weight_difference = measured_weight - cat_profile.baseline_weight
        
        # Use event's data_source if not provided
        if data_source is None:
            data_source = event.data_source
        
        # Create measurement
        measurement = WeightMeasurement(
            measurement_id=str(uuid.uuid4()),
            cat_id=cat_profile.cat_id,
            event_id=event.event_id,
            measured_weight=measured_weight,
            profile_weight=cat_profile.baseline_weight,
            weight_difference=weight_difference,
            timestamp=event.start_time,
            data_source=data_source
        )
        
        # Save to database
        self.db.save_weight_measurement(measurement)
        
        logger.info(f"Recorded weight measurement for {cat_profile.name}: "
                   f"{measured_weight:.2f}kg (profile: {cat_profile.baseline_weight:.2f}kg, "
                   f"diff: {weight_difference:+.2f}kg)")
        
        return measurement
    
    def get_weight_history(self, cat_id: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[WeightMeasurement]:
        """
        Get weight history for a cat
        
        Args:
            cat_id: Cat ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of weight measurements sorted by timestamp (chronological order)
        """
        return self.db.get_weight_history(cat_id, start_date, end_date)
    
    def calculate_weight_change_rate(self, cat_id: str, days: int) -> Optional[float]:
        """
        Calculate weight change rate over period (percentage)
        
        Args:
            cat_id: Cat ID
            days: Number of days to look back
            
        Returns:
            Weight change rate as percentage, or None if insufficient data
        """
        # Get measurements from the last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        measurements = self.get_weight_history(cat_id, start_date, end_date)
        
        if len(measurements) < 2:
            logger.debug(f"Insufficient measurements for cat {cat_id} over {days} days")
            return None
        
        # Get earliest and most recent measurements
        earliest = measurements[0]
        latest = measurements[-1]
        
        # Calculate percentage change
        if earliest.measured_weight == 0:
            logger.warning(f"Earliest measurement has zero weight for cat {cat_id}")
            return None
        
        change_rate = ((latest.measured_weight - earliest.measured_weight) / 
                      earliest.measured_weight) * 100
        
        logger.debug(f"Weight change rate for cat {cat_id} over {days} days: {change_rate:+.1f}%")
        
        return change_rate
    
    def get_latest_measurement(self, cat_id: str) -> Optional[WeightMeasurement]:
        """
        Get most recent weight measurement
        
        Args:
            cat_id: Cat ID
            
        Returns:
            Latest WeightMeasurement or None
        """
        return self.db.get_latest_measurement(cat_id)
