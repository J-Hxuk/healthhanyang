"""
Unit tests for data schema models
"""

import unittest
from datetime import datetime
from src.data.schema import WeightMeasurement, DataSourceMode, Event, EventType, BaselineHistory


class TestWeightMeasurement(unittest.TestCase):
    """Test WeightMeasurement data model"""

    def setUp(self):
        """Set up test data"""
        self.test_timestamp = datetime(2024, 1, 15, 10, 30, 0)
        self.test_measurement = WeightMeasurement(
            measurement_id="test-measurement-123",
            cat_id="cat-456",
            event_id="event-789",
            measured_weight=4.5,
            profile_weight=4.2,
            weight_difference=0.3,
            timestamp=self.test_timestamp,
            data_source=DataSourceMode.SIMULATION
        )

    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = self.test_measurement.to_dict()
        
        self.assertEqual(result['measurement_id'], "test-measurement-123")
        self.assertEqual(result['cat_id'], "cat-456")
        self.assertEqual(result['event_id'], "event-789")
        self.assertEqual(result['measured_weight'], 4.5)
        self.assertEqual(result['profile_weight'], 4.2)
        self.assertEqual(result['weight_difference'], 0.3)
        self.assertEqual(result['timestamp'], self.test_timestamp.isoformat())
        self.assertEqual(result['data_source'], "simulation")

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'measurement_id': "test-measurement-123",
            'cat_id': "cat-456",
            'event_id': "event-789",
            'measured_weight': 4.5,
            'profile_weight': 4.2,
            'weight_difference': 0.3,
            'timestamp': self.test_timestamp.isoformat(),
            'data_source': "simulation"
        }
        
        result = WeightMeasurement.from_dict(data)
        
        self.assertEqual(result.measurement_id, "test-measurement-123")
        self.assertEqual(result.cat_id, "cat-456")
        self.assertEqual(result.event_id, "event-789")
        self.assertEqual(result.measured_weight, 4.5)
        self.assertEqual(result.profile_weight, 4.2)
        self.assertEqual(result.weight_difference, 0.3)
        self.assertEqual(result.timestamp, self.test_timestamp)
        self.assertEqual(result.data_source, DataSourceMode.SIMULATION)

    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        dict_data = self.test_measurement.to_dict()
        reconstructed = WeightMeasurement.from_dict(dict_data)
        
        self.assertEqual(reconstructed.measurement_id, self.test_measurement.measurement_id)
        self.assertEqual(reconstructed.cat_id, self.test_measurement.cat_id)
        self.assertEqual(reconstructed.event_id, self.test_measurement.event_id)
        self.assertEqual(reconstructed.measured_weight, self.test_measurement.measured_weight)
        self.assertEqual(reconstructed.profile_weight, self.test_measurement.profile_weight)
        self.assertEqual(reconstructed.weight_difference, self.test_measurement.weight_difference)
        self.assertEqual(reconstructed.timestamp, self.test_measurement.timestamp)
        self.assertEqual(reconstructed.data_source, self.test_measurement.data_source)

    def test_sensor_data_source(self):
        """Test WeightMeasurement with sensor data source"""
        measurement = WeightMeasurement(
            measurement_id="sensor-measurement-001",
            cat_id="cat-123",
            event_id="event-456",
            measured_weight=3.8,
            profile_weight=4.0,
            weight_difference=-0.2,
            timestamp=datetime.now(),
            data_source=DataSourceMode.SENSOR
        )
        
        dict_data = measurement.to_dict()
        self.assertEqual(dict_data['data_source'], "sensor")
        
        reconstructed = WeightMeasurement.from_dict(dict_data)
        self.assertEqual(reconstructed.data_source, DataSourceMode.SENSOR)

    def test_negative_weight_difference(self):
        """Test WeightMeasurement with negative weight difference (weight loss)"""
        measurement = WeightMeasurement(
            measurement_id="loss-measurement-001",
            cat_id="cat-789",
            event_id="event-012",
            measured_weight=3.5,
            profile_weight=4.0,
            weight_difference=-0.5,
            timestamp=datetime.now(),
            data_source=DataSourceMode.SIMULATION
        )
        
        self.assertEqual(measurement.weight_difference, -0.5)
        
        dict_data = measurement.to_dict()
        reconstructed = WeightMeasurement.from_dict(dict_data)
        self.assertEqual(reconstructed.weight_difference, -0.5)


if __name__ == '__main__':
    unittest.main()


class TestEvent(unittest.TestCase):
    """Test Event data model with data_source field"""

    def setUp(self):
        """Set up test data"""
        self.test_start_time = datetime(2024, 1, 15, 10, 30, 0)
        self.test_end_time = datetime(2024, 1, 15, 10, 32, 0)
        self.test_event = Event(
            event_id="event-123",
            device_id="device-456",
            cat_id="cat-789",
            event_type=EventType.CAT_VISIT,
            start_time=self.test_start_time,
            end_time=self.test_end_time,
            duration=120.0,
            baseline_before=2.5,
            baseline_after=2.5,
            max_weight=6.8,
            avg_weight=6.5,
            weight_gain=4.0,
            baseline_shift=0.0,
            stability_score=0.95,
            confidence_score=0.88,
            data_source=DataSourceMode.SIMULATION
        )

    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = self.test_event.to_dict()
        
        self.assertEqual(result['event_id'], "event-123")
        self.assertEqual(result['device_id'], "device-456")
        self.assertEqual(result['cat_id'], "cat-789")
        self.assertEqual(result['event_type'], "cat_visit")
        self.assertEqual(result['start_time'], self.test_start_time.isoformat())
        self.assertEqual(result['end_time'], self.test_end_time.isoformat())
        self.assertEqual(result['duration'], 120.0)
        self.assertEqual(result['baseline_before'], 2.5)
        self.assertEqual(result['baseline_after'], 2.5)
        self.assertEqual(result['max_weight'], 6.8)
        self.assertEqual(result['avg_weight'], 6.5)
        self.assertEqual(result['weight_gain'], 4.0)
        self.assertEqual(result['baseline_shift'], 0.0)
        self.assertEqual(result['stability_score'], 0.95)
        self.assertEqual(result['confidence_score'], 0.88)
        self.assertEqual(result['data_source'], "simulation")

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'event_id': "event-123",
            'device_id': "device-456",
            'cat_id': "cat-789",
            'event_type': "cat_visit",
            'start_time': self.test_start_time.isoformat(),
            'end_time': self.test_end_time.isoformat(),
            'duration': 120.0,
            'baseline_before': 2.5,
            'baseline_after': 2.5,
            'max_weight': 6.8,
            'avg_weight': 6.5,
            'weight_gain': 4.0,
            'baseline_shift': 0.0,
            'stability_score': 0.95,
            'confidence_score': 0.88,
            'data_source': "simulation"
        }
        
        result = Event.from_dict(data)
        
        self.assertEqual(result.event_id, "event-123")
        self.assertEqual(result.device_id, "device-456")
        self.assertEqual(result.cat_id, "cat-789")
        self.assertEqual(result.event_type, EventType.CAT_VISIT)
        self.assertEqual(result.start_time, self.test_start_time)
        self.assertEqual(result.end_time, self.test_end_time)
        self.assertEqual(result.duration, 120.0)
        self.assertEqual(result.baseline_before, 2.5)
        self.assertEqual(result.baseline_after, 2.5)
        self.assertEqual(result.max_weight, 6.8)
        self.assertEqual(result.avg_weight, 6.5)
        self.assertEqual(result.weight_gain, 4.0)
        self.assertEqual(result.baseline_shift, 0.0)
        self.assertEqual(result.stability_score, 0.95)
        self.assertEqual(result.confidence_score, 0.88)
        self.assertEqual(result.data_source, DataSourceMode.SIMULATION)

    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        dict_data = self.test_event.to_dict()
        reconstructed = Event.from_dict(dict_data)
        
        self.assertEqual(reconstructed.event_id, self.test_event.event_id)
        self.assertEqual(reconstructed.device_id, self.test_event.device_id)
        self.assertEqual(reconstructed.cat_id, self.test_event.cat_id)
        self.assertEqual(reconstructed.event_type, self.test_event.event_type)
        self.assertEqual(reconstructed.start_time, self.test_event.start_time)
        self.assertEqual(reconstructed.end_time, self.test_event.end_time)
        self.assertEqual(reconstructed.duration, self.test_event.duration)
        self.assertEqual(reconstructed.baseline_before, self.test_event.baseline_before)
        self.assertEqual(reconstructed.baseline_after, self.test_event.baseline_after)
        self.assertEqual(reconstructed.max_weight, self.test_event.max_weight)
        self.assertEqual(reconstructed.avg_weight, self.test_event.avg_weight)
        self.assertEqual(reconstructed.weight_gain, self.test_event.weight_gain)
        self.assertEqual(reconstructed.baseline_shift, self.test_event.baseline_shift)
        self.assertEqual(reconstructed.stability_score, self.test_event.stability_score)
        self.assertEqual(reconstructed.confidence_score, self.test_event.confidence_score)
        self.assertEqual(reconstructed.data_source, self.test_event.data_source)

    def test_sensor_data_source(self):
        """Test Event with sensor data source"""
        event = Event(
            event_id="sensor-event-001",
            device_id="device-001",
            cat_id="cat-001",
            event_type=EventType.CAT_VISIT,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=60.0,
            baseline_before=2.0,
            baseline_after=2.0,
            max_weight=6.0,
            avg_weight=5.8,
            weight_gain=3.8,
            baseline_shift=0.0,
            stability_score=0.9,
            confidence_score=0.85,
            data_source=DataSourceMode.SENSOR
        )
        
        dict_data = event.to_dict()
        self.assertEqual(dict_data['data_source'], "sensor")
        
        reconstructed = Event.from_dict(dict_data)
        self.assertEqual(reconstructed.data_source, DataSourceMode.SENSOR)

    def test_event_without_cat_id(self):
        """Test Event with no cat identified (cat_id is None)"""
        event = Event(
            event_id="unknown-event-001",
            device_id="device-001",
            cat_id=None,
            event_type=EventType.UNKNOWN,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=30.0,
            baseline_before=2.0,
            baseline_after=2.0,
            max_weight=5.0,
            avg_weight=4.8,
            weight_gain=2.8,
            baseline_shift=0.0,
            stability_score=0.7,
            confidence_score=0.5,
            data_source=DataSourceMode.SIMULATION
        )
        
        dict_data = event.to_dict()
        self.assertIsNone(dict_data['cat_id'])
        
        reconstructed = Event.from_dict(dict_data)
        self.assertIsNone(reconstructed.cat_id)

    def test_backward_compatibility_without_data_source(self):
        """Test Event.from_dict with legacy data (no data_source field)"""
        # Simulate legacy event data without data_source field
        legacy_data = {
            'event_id': "legacy-event-001",
            'device_id': "device-001",
            'cat_id': "cat-001",
            'event_type': "cat_visit",
            'start_time': datetime(2024, 1, 15, 10, 30, 0).isoformat(),
            'end_time': datetime(2024, 1, 15, 10, 32, 0).isoformat(),
            'duration': 120.0,
            'baseline_before': 2.5,
            'baseline_after': 2.5,
            'max_weight': 6.8,
            'avg_weight': 6.5,
            'weight_gain': 4.0,
            'baseline_shift': 0.0,
            'stability_score': 0.95,
            'confidence_score': 0.88
            # Note: no 'data_source' field
        }
        
        # Should default to SIMULATION
        event = Event.from_dict(legacy_data)
        self.assertEqual(event.data_source, DataSourceMode.SIMULATION)
        self.assertEqual(event.event_id, "legacy-event-001")



class TestBaselineHistory(unittest.TestCase):
    """Test BaselineHistory data model"""

    def setUp(self):
        """Set up test data"""
        self.test_timestamp = datetime(2024, 1, 15, 10, 30, 0)
        self.test_baseline_history = BaselineHistory(
            id="baseline-history-123",
            device_id="device-456",
            baseline_weight=2.8,
            timestamp=self.test_timestamp,
            reason="litter_refill",
            previous_weight=2.0,
            change_amount=0.8,
            data_source=DataSourceMode.SIMULATION
        )

    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = self.test_baseline_history.to_dict()
        
        self.assertEqual(result['id'], "baseline-history-123")
        self.assertEqual(result['device_id'], "device-456")
        self.assertEqual(result['baseline_weight'], 2.8)
        self.assertEqual(result['timestamp'], self.test_timestamp.isoformat())
        self.assertEqual(result['reason'], "litter_refill")
        self.assertEqual(result['previous_weight'], 2.0)
        self.assertEqual(result['change_amount'], 0.8)
        self.assertEqual(result['data_source'], "simulation")

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'id': "baseline-history-123",
            'device_id': "device-456",
            'baseline_weight': 2.8,
            'timestamp': self.test_timestamp.isoformat(),
            'reason': "litter_refill",
            'previous_weight': 2.0,
            'change_amount': 0.8,
            'data_source': "simulation"
        }
        
        result = BaselineHistory.from_dict(data)
        
        self.assertEqual(result.id, "baseline-history-123")
        self.assertEqual(result.device_id, "device-456")
        self.assertEqual(result.baseline_weight, 2.8)
        self.assertEqual(result.timestamp, self.test_timestamp)
        self.assertEqual(result.reason, "litter_refill")
        self.assertEqual(result.previous_weight, 2.0)
        self.assertEqual(result.change_amount, 0.8)
        self.assertEqual(result.data_source, DataSourceMode.SIMULATION)

    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        dict_data = self.test_baseline_history.to_dict()
        reconstructed = BaselineHistory.from_dict(dict_data)
        
        self.assertEqual(reconstructed.id, self.test_baseline_history.id)
        self.assertEqual(reconstructed.device_id, self.test_baseline_history.device_id)
        self.assertEqual(reconstructed.baseline_weight, self.test_baseline_history.baseline_weight)
        self.assertEqual(reconstructed.timestamp, self.test_baseline_history.timestamp)
        self.assertEqual(reconstructed.reason, self.test_baseline_history.reason)
        self.assertEqual(reconstructed.previous_weight, self.test_baseline_history.previous_weight)
        self.assertEqual(reconstructed.change_amount, self.test_baseline_history.change_amount)
        self.assertEqual(reconstructed.data_source, self.test_baseline_history.data_source)

    def test_sensor_data_source(self):
        """Test BaselineHistory with sensor data source"""
        baseline_history = BaselineHistory(
            id="sensor-baseline-001",
            device_id="device-001",
            baseline_weight=3.0,
            timestamp=datetime.now(),
            reason="cleaning",
            previous_weight=3.3,
            change_amount=-0.3,
            data_source=DataSourceMode.SENSOR
        )
        
        dict_data = baseline_history.to_dict()
        self.assertEqual(dict_data['data_source'], "sensor")
        
        reconstructed = BaselineHistory.from_dict(dict_data)
        self.assertEqual(reconstructed.data_source, DataSourceMode.SENSOR)

    def test_negative_change_amount(self):
        """Test BaselineHistory with negative change amount (cleaning/waste removal)"""
        baseline_history = BaselineHistory(
            id="cleaning-baseline-001",
            device_id="device-001",
            baseline_weight=2.5,
            timestamp=datetime.now(),
            reason="cleaning",
            previous_weight=2.8,
            change_amount=-0.3,
            data_source=DataSourceMode.SIMULATION
        )
        
        self.assertEqual(baseline_history.change_amount, -0.3)
        
        dict_data = baseline_history.to_dict()
        reconstructed = BaselineHistory.from_dict(dict_data)
        self.assertEqual(reconstructed.change_amount, -0.3)

    def test_various_reasons(self):
        """Test BaselineHistory with different reasons"""
        reasons = ["stable", "cleaning", "litter_refill", "user_reset"]
        
        for reason in reasons:
            baseline_history = BaselineHistory(
                id=f"baseline-{reason}",
                device_id="device-001",
                baseline_weight=2.5,
                timestamp=datetime.now(),
                reason=reason,
                previous_weight=2.3,
                change_amount=0.2,
                data_source=DataSourceMode.SIMULATION
            )
            
            dict_data = baseline_history.to_dict()
            reconstructed = BaselineHistory.from_dict(dict_data)
            self.assertEqual(reconstructed.reason, reason)
