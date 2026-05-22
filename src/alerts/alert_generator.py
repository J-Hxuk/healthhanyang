"""
Alert Generator Module

Generates health alerts based on weight changes and visit patterns
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from ..data.schema import CatProfile, WeightChangeAlert
from ..storage.database import Database
from ..tracking.weight_tracker import WeightTracker


logger = logging.getLogger(__name__)


class AlertGenerator:
    """Generates health alerts based on weight changes"""
    
    # Alert thresholds
    WARNING_THRESHOLD_7D = 5.0  # 5% over 7 days
    CRITICAL_THRESHOLD_7D = 10.0  # 10% over 7 days
    CRITICAL_THRESHOLD_SHORT = 7.5  # 7.5% over <7 days
    NORMAL_CHANGE_RATE = 2.0  # ±2% per week is normal
    
    # Duplicate prevention window
    DUPLICATE_WINDOW_HOURS = 24
    
    def __init__(self, database: Database, weight_tracker: WeightTracker):
        """
        Initialize alert generator
        
        Args:
            database: Database instance
            weight_tracker: WeightTracker instance
        """
        self.db = database
        self.weight_tracker = weight_tracker
        self.alert_cache: Dict[str, datetime] = {}  # cat_id -> last_alert_time
    
    def check_weight_change_alerts(self, cat_id: str) -> Optional[WeightChangeAlert]:
        """
        Check for weight change alerts for a cat
        
        Args:
            cat_id: Cat ID
            
        Returns:
            WeightChangeAlert if alert should be created, None otherwise
        """
        # Get cat profile
        cat_profile = self.db.get_cat_profile(cat_id)
        if not cat_profile:
            logger.warning(f"Cat profile not found for {cat_id}")
            return None
        
        # Check 7-day change rate
        change_rate_7d = self.weight_tracker.calculate_weight_change_rate(cat_id, 7)
        
        if change_rate_7d is not None:
            severity = self.should_create_alert(cat_id, change_rate_7d, 7)
            if severity:
                return self.create_alert(cat_profile, change_rate_7d, 7, severity)
        
        # Check shorter periods for critical changes
        for days in [3, 5]:
            change_rate = self.weight_tracker.calculate_weight_change_rate(cat_id, days)
            if change_rate is not None:
                abs_change = abs(change_rate)
                if abs_change > self.CRITICAL_THRESHOLD_SHORT:
                    severity = "critical"
                    if not self.is_duplicate_alert(cat_id, "weight_change"):
                        return self.create_alert(cat_profile, change_rate, days, severity)
        
        return None
    
    def should_create_alert(self, cat_id: str, change_rate: float, days: int) -> Optional[str]:
        """
        Determine if alert should be created (returns severity)
        
        Args:
            cat_id: Cat ID
            change_rate: Weight change rate (percentage)
            days: Time period in days
            
        Returns:
            Severity level ("warning" or "critical") or None
        """
        abs_change = abs(change_rate)
        
        # Check for duplicate alerts
        if self.is_duplicate_alert(cat_id, "weight_change"):
            logger.debug(f"Duplicate alert prevented for cat {cat_id}")
            return None
        
        # 7-day thresholds
        if days == 7:
            if abs_change > self.CRITICAL_THRESHOLD_7D:
                return "critical"
            elif abs_change > self.WARNING_THRESHOLD_7D:
                return "warning"
        
        # Short-term critical threshold
        elif days < 7:
            if abs_change > self.CRITICAL_THRESHOLD_SHORT:
                return "critical"
        
        return None
    
    def create_alert(self, cat_profile: CatProfile, change_rate: float,
                    days: int, severity: str) -> WeightChangeAlert:
        """
        Create weight change alert
        
        Args:
            cat_profile: Cat profile
            change_rate: Weight change rate (percentage)
            days: Time period in days
            severity: Alert severity ("warning" or "critical")
            
        Returns:
            Created WeightChangeAlert
        """
        # Get latest measurement
        latest = self.weight_tracker.get_latest_measurement(cat_profile.cat_id)
        current_weight = latest.measured_weight if latest else cat_profile.baseline_weight
        
        # Determine if change is abnormal
        is_abnormal = abs(change_rate) > self.NORMAL_CHANGE_RATE
        direction = "증가" if change_rate > 0 else "감소"
        
        # Create message
        if severity == "critical":
            message = (f"⚠️ 위험: {cat_profile.name}의 체중이 {days}일 동안 {abs(change_rate):.1f}% {direction}했습니다. "
                      f"즉시 수의사 상담을 권장합니다.")
        else:
            message = (f"⚠️ 주의: {cat_profile.name}의 체중이 {days}일 동안 {abs(change_rate):.1f}% {direction}했습니다. "
                      f"계속 모니터링하세요.")
        
        # Create details
        details = {
            'profile_weight': cat_profile.baseline_weight,
            'current_weight': current_weight,
            'weight_difference': current_weight - cat_profile.baseline_weight,
            'is_abnormal': is_abnormal,
            'normal_change_rate': self.NORMAL_CHANGE_RATE,
            'recommended_action': '수의사 상담' if severity == 'critical' else '계속 모니터링'
        }
        
        # Create alert
        alert = WeightChangeAlert(
            alert_id=str(uuid.uuid4()),
            cat_id=cat_profile.cat_id,
            cat_name=cat_profile.name,
            alert_type="weight_change",
            severity=severity,
            message=message,
            details=details,
            timestamp=datetime.now(),
            weight_change_rate=change_rate,
            time_period_days=days
        )
        
        # Save to database
        self.db.save_weight_change_alert(alert)
        
        # Update cache
        self.alert_cache[cat_profile.cat_id] = datetime.now()
        
        logger.info(f"Created {severity} weight change alert for {cat_profile.name}: "
                   f"{change_rate:+.1f}% over {days} days")
        
        return alert
    
    def is_duplicate_alert(self, cat_id: str, alert_type: str) -> bool:
        """
        Check if alert was created in last 24 hours
        
        Args:
            cat_id: Cat ID
            alert_type: Alert type
            
        Returns:
            True if duplicate, False otherwise
        """
        # Check cache first
        if cat_id in self.alert_cache:
            last_alert_time = self.alert_cache[cat_id]
            time_since_last = datetime.now() - last_alert_time
            if time_since_last < timedelta(hours=self.DUPLICATE_WINDOW_HOURS):
                return True
        
        # Check database for recent alerts
        recent_alerts = self.db.get_weight_change_alerts(cat_id, limit=5)
        for alert in recent_alerts:
            time_since_alert = datetime.now() - alert.timestamp
            if time_since_alert < timedelta(hours=self.DUPLICATE_WINDOW_HOURS):
                # Update cache
                self.alert_cache[cat_id] = alert.timestamp
                return True
        
        return False
