"""
Quick implementation test
"""

import sys
from datetime import datetime

# Test imports
print("Testing imports...")
from src.data.schema import (
    WeightMeasurement, DataSourceMode, BaselineHistory,
    SensorConnectionInfo, ConnectionStatus,
    SimulationConfig, SimulationResult, SimulationScenario,
    WeightChangeAlert
)
from src.storage.database import Database
from src.tracking.weight_tracker import WeightTracker
from src.alerts.alert_generator import AlertGenerator
from src.simulation import (
    DataSourceInterface, SensorConnection, SimulationGenerator,
    BaselineSimulator, LongTermSimulator
)

print("✅ All imports successful!")

# Test WeightMeasurement
print("\nTesting WeightMeasurement...")
measurement = WeightMeasurement(
    measurement_id="test-1",
    cat_id="cat-1",
    event_id="event-1",
    measured_weight=4.5,
    profile_weight=4.2,
    weight_difference=0.3,
    timestamp=datetime.now(),
    data_source=DataSourceMode.SIMULATION
)
data = measurement.to_dict()
reconstructed = WeightMeasurement.from_dict(data)
assert reconstructed.measured_weight == 4.5
print("✅ WeightMeasurement works!")

# Test BaselineHistory
print("\nTesting BaselineHistory...")
history = BaselineHistory(
    id="hist-1",
    device_id="device-1",
    baseline_weight=2.5,
    timestamp=datetime.now(),
    reason="stable",
    previous_weight=2.4,
    change_amount=0.1,
    data_source=DataSourceMode.SIMULATION
)
data = history.to_dict()
reconstructed = BaselineHistory.from_dict(data)
assert reconstructed.change_amount == 0.1
print("✅ BaselineHistory works!")

# Test SensorConnectionInfo
print("\nTesting SensorConnectionInfo...")
conn_info = SensorConnectionInfo(
    device_id="sensor-1",
    status=ConnectionStatus.CONNECTED,
    last_received=datetime.now(),
    last_weight=2.5,
    connection_time=datetime.now(),
    error_message=None
)
data = conn_info.to_dict()
reconstructed = SensorConnectionInfo.from_dict(data)
assert reconstructed.status == ConnectionStatus.CONNECTED
print("✅ SensorConnectionInfo works!")

# Test SimulationConfig
print("\nTesting SimulationConfig...")
config = SimulationConfig(
    duration_days=7,
    start_datetime=datetime.now(),
    cats=[("cat-1", SimulationScenario.NORMAL)]
)
data = config.to_dict()
reconstructed = SimulationConfig.from_dict(data)
assert reconstructed.duration_days == 7
print("✅ SimulationConfig works!")

# Test WeightChangeAlert
print("\nTesting WeightChangeAlert...")
alert = WeightChangeAlert(
    alert_id="alert-1",
    cat_id="cat-1",
    cat_name="나비",
    alert_type="weight_change",
    severity="warning",
    message="체중 변화 감지",
    details={},
    timestamp=datetime.now(),
    weight_change_rate=5.5,
    time_period_days=7
)
data = alert.to_dict()
reconstructed = WeightChangeAlert.from_dict(data)
assert reconstructed.weight_change_rate == 5.5
print("✅ WeightChangeAlert works!")

# Test Database
print("\nTesting Database...")
db = Database("test_data")
print("✅ Database initialized!")

# Test WeightTracker
print("\nTesting WeightTracker...")
tracker = WeightTracker(db)
print("✅ WeightTracker initialized!")

# Test AlertGenerator
print("\nTesting AlertGenerator...")
alert_gen = AlertGenerator(db, tracker)
print("✅ AlertGenerator initialized!")

# Test DataSourceInterface
print("\nTesting DataSourceInterface...")
dsi = DataSourceInterface()
dsi.set_mode(DataSourceMode.SIMULATION)
assert dsi.mode == DataSourceMode.SIMULATION
print("✅ DataSourceInterface works!")

# Test SimulationGenerator
print("\nTesting SimulationGenerator...")
sim_gen = SimulationGenerator("device-1")
sim_gen.set_baseline(2.5)
sim_gen.simulate_cat_entry(4.0)
data_point = sim_gen.generate_data_point()
assert data_point.total_weight > 6.0  # baseline + cat
print("✅ SimulationGenerator works!")

print("\n" + "="*50)
print("🎉 All tests passed!")
print("="*50)
