"""
Health Monitoring Module

Detects abnormal patterns including frequent urination (빈뇨)
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from dataclasses import dataclass
import statistics

from ..data.schema import Event, EventType, CatProfile


@dataclass
class HealthAlert:
    """Health alert information"""
    alert_id: str
    cat_id: str
    cat_name: str
    alert_type: str  # "frequent_urination", "weight_change", "behavior_change"
    severity: str  # "info", "warning", "critical"
    message: str
    details: str
    timestamp: datetime
    visit_count: int = 0
    avg_duration: float = 0.0


class HealthMonitor:
    """Monitors cat health patterns and detects abnormalities"""
    
    def __init__(self):
        # Thresholds for frequent urination detection
        self.normal_daily_visits = 4  # Normal: 2-4 visits per day
        self.warning_daily_visits = 6  # Warning: 6+ visits
        self.critical_daily_visits = 8  # Critical: 8+ visits
        
        self.normal_visit_duration = (30, 120)  # Normal: 30-120 seconds
        self.short_visit_threshold = 30  # Short visit: < 30 seconds
        
        # Pattern change detection
        self.baseline_days = 7  # Use 7 days for baseline
        self.significant_increase = 1.5  # 50% increase is significant
    
    def check_frequent_urination(
        self, 
        cat_profile: CatProfile,
        today_events: List[Event],
        recent_events: List[Event]
    ) -> Optional[HealthAlert]:
        """
        Check for frequent urination pattern
        
        Args:
            cat_profile: Cat profile information
            today_events: Today's events for this cat
            recent_events: Recent events (last 7 days) for baseline
            
        Returns:
            HealthAlert if abnormal pattern detected, None otherwise
        """
        import uuid
        
        # Count today's visits
        today_visit_count = len(today_events)
        
        if today_visit_count == 0:
            return None
        
        # Calculate average visit duration
        durations = [event.duration for event in today_events]
        avg_duration = statistics.mean(durations)
        short_visits = sum(1 for d in durations if d < self.short_visit_threshold)
        
        # Calculate baseline (average daily visits over past week)
        baseline_daily_avg = self._calculate_baseline_visits(recent_events)
        
        # Detect frequent urination patterns
        severity = None
        message = ""
        details = ""
        
        # Pattern 1: High absolute visit count
        if today_visit_count >= self.critical_daily_visits:
            severity = "critical"
            message = f"⚠️ {cat_profile.name}의 화장실 방문이 매우 잦습니다"
            details = (
                f"오늘 {today_visit_count}회 방문 (정상: 2-4회)\n"
                f"평균 체류 시간: {avg_duration:.0f}초\n"
                f"짧은 방문 ({self.short_visit_threshold}초 미만): {short_visits}회\n\n"
                f"💡 가능한 원인:\n"
                f"- 빈뇨 (방광염, 요로결석, 당뇨병 등)\n"
                f"- 스트레스\n"
                f"- 행동 문제\n\n"
                f"⚕️ 권장사항: 수의사 상담을 권장합니다"
            )
        
        elif today_visit_count >= self.warning_daily_visits:
            severity = "warning"
            message = f"⚠️ {cat_profile.name}의 화장실 방문이 잦습니다"
            details = (
                f"오늘 {today_visit_count}회 방문 (정상: 2-4회)\n"
                f"평균 체류 시간: {avg_duration:.0f}초\n"
                f"짧은 방문: {short_visits}회\n\n"
                f"💡 관찰이 필요합니다. 내일도 계속되면 수의사 상담을 권장합니다."
            )
        
        # Pattern 2: Significant increase from baseline
        elif baseline_daily_avg > 0 and today_visit_count >= baseline_daily_avg * self.significant_increase:
            severity = "warning"
            increase_pct = ((today_visit_count / baseline_daily_avg) - 1) * 100
            message = f"📈 {cat_profile.name}의 방문 패턴이 변화했습니다"
            details = (
                f"오늘 {today_visit_count}회 방문\n"
                f"평소 평균: {baseline_daily_avg:.1f}회/일\n"
                f"증가율: +{increase_pct:.0f}%\n\n"
                f"💡 평소보다 {increase_pct:.0f}% 증가했습니다. 계속 관찰해주세요."
            )
        
        # Pattern 3: Many short visits (possible urinary urgency)
        elif short_visits >= 3 and short_visits / today_visit_count >= 0.5:
            severity = "warning"
            message = f"⏱️ {cat_profile.name}의 짧은 방문이 많습니다"
            details = (
                f"오늘 {today_visit_count}회 방문 중 {short_visits}회가 짧은 방문\n"
                f"평균 체류 시간: {avg_duration:.0f}초\n\n"
                f"💡 소변을 자주 보려고 하지만 조금씩만 나오는 것일 수 있습니다.\n"
                f"빈뇨 증상일 가능성이 있으니 관찰해주세요."
            )
        
        if severity:
            return HealthAlert(
                alert_id=str(uuid.uuid4()),
                cat_id=cat_profile.cat_id,
                cat_name=cat_profile.name,
                alert_type="frequent_urination",
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(),
                visit_count=today_visit_count,
                avg_duration=avg_duration
            )
        
        return None
    
    def _calculate_baseline_visits(self, recent_events: List[Event]) -> float:
        """
        Calculate baseline daily visit count from recent events
        
        Args:
            recent_events: Events from past 7 days
            
        Returns:
            Average daily visit count
        """
        if not recent_events:
            return 0.0
        
        # Group events by date
        events_by_date = {}
        for event in recent_events:
            date_key = event.start_time.date()
            if date_key not in events_by_date:
                events_by_date[date_key] = 0
            events_by_date[date_key] += 1
        
        # Calculate average
        if events_by_date:
            return statistics.mean(events_by_date.values())
        
        return 0.0
    
    def get_health_summary(
        self,
        cat_profile: CatProfile,
        today_events: List[Event],
        recent_events: List[Event]
    ) -> dict:
        """
        Get comprehensive health summary for a cat
        
        Returns:
            Dictionary with health metrics and status
        """
        today_count = len(today_events)
        baseline_avg = self._calculate_baseline_visits(recent_events)
        
        if today_events:
            durations = [e.duration for e in today_events]
            avg_duration = statistics.mean(durations)
            short_visits = sum(1 for d in durations if d < self.short_visit_threshold)
        else:
            avg_duration = 0
            short_visits = 0
        
        # Determine status
        if today_count >= self.critical_daily_visits:
            status = "critical"
            status_text = "⚠️ 즉시 확인 필요"
        elif today_count >= self.warning_daily_visits:
            status = "warning"
            status_text = "⚠️ 주의 필요"
        elif baseline_avg > 0 and today_count >= baseline_avg * self.significant_increase:
            status = "warning"
            status_text = "📈 패턴 변화 감지"
        else:
            status = "normal"
            status_text = "✅ 정상"
        
        return {
            "status": status,
            "status_text": status_text,
            "today_visits": today_count,
            "baseline_avg": baseline_avg,
            "avg_duration": avg_duration,
            "short_visits": short_visits,
            "normal_range": f"{self.normal_daily_visits}회 이하",
            "warning_threshold": f"{self.warning_daily_visits}회 이상",
            "critical_threshold": f"{self.critical_daily_visits}회 이상"
        }
