"""
Database Module

Simple JSON-based storage for development
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..data.schema import (
    RawSensorData, ProcessedSensorData, Event, CatProfile,
    Alert, BaselineHistory, EventType
)


logger = logging.getLogger(__name__)


class Database:
    """Simple JSON-based database"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize database
        
        Args:
            data_dir: Directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)
        (self.data_dir / "events").mkdir(exist_ok=True)
        (self.data_dir / "profiles").mkdir(exist_ok=True)
        (self.data_dir / "alerts").mkdir(exist_ok=True)
        (self.data_dir / "baseline").mkdir(exist_ok=True)
    
    def save_raw_sensor_data(self, data: RawSensorData):
        """Save raw sensor data"""
        file_path = self.data_dir / "raw" / f"{data.id}.json"
        with open(file_path, 'w') as f:
            json.dump(data.to_dict(), f, indent=2)
    
    def save_processed_sensor_data(self, data: ProcessedSensorData):
        """Save processed sensor data"""
        file_path = self.data_dir / "processed" / f"{data.id}.json"
        with open(file_path, 'w') as f:
            json.dump(data.to_dict(), f, indent=2)
    
    def save_event(self, event: Event):
        """Save event"""
        file_path = self.data_dir / "events" / f"{event.event_id}.json"
        with open(file_path, 'w') as f:
            json.dump(event.to_dict(), f, indent=2)
        logger.info(f"Saved event: {event.event_id} ({event.event_type.value})")
    
    def get_events(self, cat_id: Optional[str] = None, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   event_type: Optional[EventType] = None) -> List[Event]:
        """
        Get events with optional filtering
        
        Args:
            cat_id: Filter by cat ID
            start_date: Filter by start date
            end_date: Filter by end date
            event_type: Filter by event type
            
        Returns:
            List of matching events
        """
        events = []
        events_dir = self.data_dir / "events"
        
        if not events_dir.exists():
            return events
        
        for file_path in events_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    event = Event.from_dict(data)
                    
                    # Apply filters
                    if cat_id and event.cat_id != cat_id:
                        continue
                    if start_date and event.start_time < start_date:
                        continue
                    if end_date and event.start_time > end_date:
                        continue
                    if event_type and event.event_type != event_type:
                        continue
                    
                    events.append(event)
            except Exception as e:
                logger.error(f"Error loading event from {file_path}: {e}")
        
        # Sort by start time
        events.sort(key=lambda e: e.start_time, reverse=True)
        
        return events
    
    def save_cat_profile(self, profile: CatProfile):
        """Save cat profile"""
        file_path = self.data_dir / "profiles" / f"{profile.cat_id}.json"
        with open(file_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        logger.info(f"Saved cat profile: {profile.name}")
    
    def get_cat_profile(self, cat_id: str) -> Optional[CatProfile]:
        """Get cat profile by ID"""
        file_path = self.data_dir / "profiles" / f"{cat_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return CatProfile.from_dict(data)
    
    def get_all_cat_profiles(self) -> List[CatProfile]:
        """Get all cat profiles"""
        profiles = []
        profiles_dir = self.data_dir / "profiles"
        
        if not profiles_dir.exists():
            return profiles
        
        for file_path in profiles_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    profiles.append(CatProfile.from_dict(data))
            except Exception as e:
                logger.error(f"Error loading profile from {file_path}: {e}")
        
        return profiles
    
    def save_alert(self, alert: Alert):
        """Save alert"""
        file_path = self.data_dir / "alerts" / f"{alert.alert_id}.json"
        with open(file_path, 'w') as f:
            json.dump(alert.to_dict(), f, indent=2)
        logger.info(f"Saved alert: {alert.alert_level.value} for cat {alert.cat_id}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        alerts = []
        alerts_dir = self.data_dir / "alerts"
        
        if not alerts_dir.exists():
            return alerts
        
        for file_path in alerts_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    alerts.append(Alert.from_dict(data))
            except Exception as e:
                logger.error(f"Error loading alert from {file_path}: {e}")
        
        # Sort by created_at
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return alerts[:limit]
    
    def save_baseline_history(self, history: BaselineHistory):
        """Save baseline history record"""
        file_path = self.data_dir / "baseline" / f"{history.id}.json"
        with open(file_path, 'w') as f:
            json.dump(history.to_dict(), f, indent=2)
