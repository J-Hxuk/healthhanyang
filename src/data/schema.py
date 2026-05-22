"""
Data Models for Cat Health Copilot System

This module defines all core data structures used throughout the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventType(Enum):
    """Event classification types"""
    CAT_VISIT = "cat_visit"
    CLEANING = "cleaning"
    LITTER_REFILL = "litter_refill"
    NOISE = "noise"
    UNKNOWN = "unknown"


class DataSourceMode(Enum):
    """Data source mode types"""
    SIMULATION = "simulation"
    SENSOR = "sensor"


class AlertLevel(Enum):
    """Alert severity levels"""
    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"


class ConnectionStatus(Enum):
    """Sensor connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class SimulationScenario(Enum):
    """Simulation scenario types"""
    NORMAL = "normal"
    POLYURIA_ONSET = "polyuria_onset"
    GRADUAL_WEIGHT_LOSS = "gradual_weight_loss"
    COMBINED = "combined"


@dataclass
class RawSensorData:
    """Raw sensor data received from ESP32"""
    id: str
    device_id: str
    timestamp: int  # ESP32 milliseconds
    received_at: datetime
    loadcell_1: float  # kg
    loadcell_2: float  # kg
    loadcell_3: float  # kg
    loadcell_4: float  # kg
    total_weight: float  # kg

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp,
            'received_at': self.received_at.isoformat(),
            'loadcell_1': self.loadcell_1,
            'loadcell_2': self.loadcell_2,
            'loadcell_3': self.loadcell_3,
            'loadcell_4': self.loadcell_4,
            'total_weight': self.total_weight
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RawSensorData':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            device_id=data['device_id'],
            timestamp=data['timestamp'],
            received_at=datetime.fromisoformat(data['received_at']),
            loadcell_1=data['loadcell_1'],
            loadcell_2=data['loadcell_2'],
            loadcell_3=data['loadcell_3'],
            loadcell_4=data['loadcell_4'],
            total_weight=data['total_weight']
        )


@dataclass
class ProcessedSensorData:
    """Processed sensor data after filtering"""
    id: str
    raw_id: str
    filtered_weight: float  # kg
    processing_timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'raw_id': self.raw_id,
            'filtered_weight': self.filtered_weight,
            'processing_timestamp': self.processing_timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessedSensorData':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            raw_id=data['raw_id'],
            filtered_weight=data['filtered_weight'],
            processing_timestamp=datetime.fromisoformat(data['processing_timestamp'])
        )


@dataclass
class Event:
    """Detected event with classification and features"""
    event_id: str
    device_id: str
    cat_id: Optional[str]
    event_type: EventType
    start_time: datetime
    end_time: datetime
    duration: float  # seconds
    baseline_before: float  # kg
    baseline_after: float  # kg
    max_weight: float  # kg
    avg_weight: float  # kg
    weight_gain: float  # kg
    baseline_shift: float  # kg
    stability_score: float  # 0-1
    confidence_score: float  # 0-1
    data_source: DataSourceMode  # Track data origin

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'event_id': self.event_id,
            'device_id': self.device_id,
            'cat_id': self.cat_id,
            'event_type': self.event_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': self.duration,
            'baseline_before': self.baseline_before,
            'baseline_after': self.baseline_after,
            'max_weight': self.max_weight,
            'avg_weight': self.avg_weight,
            'weight_gain': self.weight_gain,
            'baseline_shift': self.baseline_shift,
            'stability_score': self.stability_score,
            'confidence_score': self.confidence_score,
            'data_source': self.data_source.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            device_id=data['device_id'],
            cat_id=data.get('cat_id'),
            event_type=EventType(data['event_type']),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            duration=data['duration'],
            baseline_before=data['baseline_before'],
            baseline_after=data['baseline_after'],
            max_weight=data['max_weight'],
            avg_weight=data['avg_weight'],
            weight_gain=data['weight_gain'],
            baseline_shift=data['baseline_shift'],
            stability_score=data['stability_score'],
            confidence_score=data['confidence_score'],
            data_source=DataSourceMode(data.get('data_source', 'simulation'))
        )


@dataclass
class CatProfile:
    """Cat profile information"""
    cat_id: str
    name: str
    baseline_weight: float  # kg
    age: Optional[int] = None  # years
    sex: Optional[str] = None  # M/F
    breed: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'cat_id': self.cat_id,
            'name': self.name,
            'baseline_weight': self.baseline_weight,
            'age': self.age,
            'sex': self.sex,
            'breed': self.breed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CatProfile':
        """Create from dictionary"""
        return cls(
            cat_id=data['cat_id'],
            name=data['name'],
            baseline_weight=data['baseline_weight'],
            age=data.get('age'),
            sex=data.get('sex'),
            breed=data.get('breed'),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class Alert:
    """Health alert notification"""
    alert_id: str
    cat_id: str
    alert_level: AlertLevel
    message: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'alert_id': self.alert_id,
            'cat_id': self.cat_id,
            'alert_level': self.alert_level.value,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Alert':
        """Create from dictionary"""
        return cls(
            alert_id=data['alert_id'],
            cat_id=data['cat_id'],
            alert_level=AlertLevel(data['alert_level']),
            message=data['message'],
            created_at=datetime.fromisoformat(data['created_at']),
            acknowledged_at=datetime.fromisoformat(data['acknowledged_at']) if data.get('acknowledged_at') else None
        )


@dataclass
class HealthAnalysis:
    """Health pattern analysis results"""
    cat_id: str
    analysis_date: datetime
    daily_visit_count_3d: float
    daily_visit_count_7d: float
    daily_visit_count_30d: float
    avg_duration_3d: float  # seconds
    avg_duration_7d: float  # seconds
    avg_duration_30d: float  # seconds
    weight_trend: str  # increasing, stable, decreasing
    pattern_change_rate: float  # percentage
    alert_level: AlertLevel

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'cat_id': self.cat_id,
            'analysis_date': self.analysis_date.isoformat(),
            'daily_visit_count_3d': self.daily_visit_count_3d,
            'daily_visit_count_7d': self.daily_visit_count_7d,
            'daily_visit_count_30d': self.daily_visit_count_30d,
            'avg_duration_3d': self.avg_duration_3d,
            'avg_duration_7d': self.avg_duration_7d,
            'avg_duration_30d': self.avg_duration_30d,
            'weight_trend': self.weight_trend,
            'pattern_change_rate': self.pattern_change_rate,
            'alert_level': self.alert_level.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HealthAnalysis':
        """Create from dictionary"""
        return cls(
            cat_id=data['cat_id'],
            analysis_date=datetime.fromisoformat(data['analysis_date']),
            daily_visit_count_3d=data['daily_visit_count_3d'],
            daily_visit_count_7d=data['daily_visit_count_7d'],
            daily_visit_count_30d=data['daily_visit_count_30d'],
            avg_duration_3d=data['avg_duration_3d'],
            avg_duration_7d=data['avg_duration_7d'],
            avg_duration_30d=data['avg_duration_30d'],
            weight_trend=data['weight_trend'],
            pattern_change_rate=data['pattern_change_rate'],
            alert_level=AlertLevel(data['alert_level'])
        )


@dataclass
class BaselineHistory:
    """Baseline weight history record"""
    id: str
    device_id: str
    baseline_weight: float  # kg
    timestamp: datetime
    reason: str  # stable, cleaning, litter_refill, user_reset
    previous_weight: float  # kg - previous baseline value
    change_amount: float  # kg - change magnitude (new - previous)
    data_source: DataSourceMode  # Track data origin

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'baseline_weight': self.baseline_weight,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'previous_weight': self.previous_weight,
            'change_amount': self.change_amount,
            'data_source': self.data_source.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BaselineHistory':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            device_id=data['device_id'],
            baseline_weight=data['baseline_weight'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            reason=data['reason'],
            previous_weight=data['previous_weight'],
            change_amount=data['change_amount'],
            data_source=DataSourceMode(data['data_source'])
        )


@dataclass
class WeightMeasurement:
    """Weight measurement record for cat weight tracking"""
    measurement_id: str
    cat_id: str
    event_id: str
    measured_weight: float  # kg
    profile_weight: float  # kg (from CatProfile at time of measurement)
    weight_difference: float  # measured - profile
    timestamp: datetime
    data_source: DataSourceMode

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'measurement_id': self.measurement_id,
            'cat_id': self.cat_id,
            'event_id': self.event_id,
            'measured_weight': self.measured_weight,
            'profile_weight': self.profile_weight,
            'weight_difference': self.weight_difference,
            'timestamp': self.timestamp.isoformat(),
            'data_source': self.data_source.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeightMeasurement':
        """Create from dictionary"""
        return cls(
            measurement_id=data['measurement_id'],
            cat_id=data['cat_id'],
            event_id=data['event_id'],
            measured_weight=data['measured_weight'],
            profile_weight=data['profile_weight'],
            weight_difference=data['weight_difference'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            data_source=DataSourceMode(data['data_source'])
        )


@dataclass
class SensorConnectionInfo:
    """Sensor connection information"""
    device_id: str
    status: ConnectionStatus
    last_received: Optional[datetime]
    last_weight: Optional[float]
    connection_time: Optional[datetime]
    error_message: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'device_id': self.device_id,
            'status': self.status.value,
            'last_received': self.last_received.isoformat() if self.last_received else None,
            'last_weight': self.last_weight,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'error_message': self.error_message
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SensorConnectionInfo':
        """Create from dictionary"""
        return cls(
            device_id=data['device_id'],
            status=ConnectionStatus(data['status']),
            last_received=datetime.fromisoformat(data['last_received']) if data.get('last_received') else None,
            last_weight=data.get('last_weight'),
            connection_time=datetime.fromisoformat(data['connection_time']) if data.get('connection_time') else None,
            error_message=data.get('error_message')
        )


@dataclass
class SimulationConfig:
    """Configuration for long-term simulation"""
    duration_days: int  # 7, 14, or 30
    start_datetime: datetime
    cats: List[tuple]  # List of (cat_id, scenario) tuples

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'duration_days': self.duration_days,
            'start_datetime': self.start_datetime.isoformat(),
            'cats': [(cat_id, scenario.value if isinstance(scenario, SimulationScenario) else scenario) 
                     for cat_id, scenario in self.cats]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SimulationConfig':
        """Create from dictionary"""
        return cls(
            duration_days=data['duration_days'],
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            cats=[(cat_id, SimulationScenario(scenario)) for cat_id, scenario in data['cats']]
        )


@dataclass
class SimulationResult:
    """Result of long-term simulation"""
    config: SimulationConfig
    events_generated: int
    alerts_created: int
    weight_changes: dict  # cat_id -> (start_weight, end_weight, change_rate)
    baseline_changes: int
    execution_time: float  # seconds
    errors: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'config': self.config.to_dict(),
            'events_generated': self.events_generated,
            'alerts_created': self.alerts_created,
            'weight_changes': self.weight_changes,
            'baseline_changes': self.baseline_changes,
            'execution_time': self.execution_time,
            'errors': self.errors
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SimulationResult':
        """Create from dictionary"""
        return cls(
            config=SimulationConfig.from_dict(data['config']),
            events_generated=data['events_generated'],
            alerts_created=data['alerts_created'],
            weight_changes=data['weight_changes'],
            baseline_changes=data['baseline_changes'],
            execution_time=data['execution_time'],
            errors=data['errors']
        )


@dataclass
class WeightChangeAlert:
    """Weight change alert notification"""
    alert_id: str
    cat_id: str
    cat_name: str
    alert_type: str  # "weight_change"
    severity: str  # "warning", "critical"
    message: str
    details: dict
    timestamp: datetime
    weight_change_rate: float
    time_period_days: int

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'alert_id': self.alert_id,
            'cat_id': self.cat_id,
            'cat_name': self.cat_name,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'weight_change_rate': self.weight_change_rate,
            'time_period_days': self.time_period_days
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeightChangeAlert':
        """Create from dictionary"""
        return cls(
            alert_id=data['alert_id'],
            cat_id=data['cat_id'],
            cat_name=data['cat_name'],
            alert_type=data['alert_type'],
            severity=data['severity'],
            message=data['message'],
            details=data['details'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            weight_change_rate=data['weight_change_rate'],
            time_period_days=data['time_period_days']
        )
