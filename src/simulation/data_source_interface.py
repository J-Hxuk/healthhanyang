"""
Data Source Interface Module

Provides uniform access to weight data regardless of source (sensor or simulation)
"""

import logging
from typing import Optional

from ..data.schema import RawSensorData, DataSourceMode, ConnectionStatus
from .sensor_connection import SensorConnection
from .simulation_generator import SimulationGenerator


logger = logging.getLogger(__name__)


class DataSourceInterface:
    """Abstracts data source (sensor vs simulation)"""
    
    def __init__(self):
        """Initialize data source interface"""
        self.mode: DataSourceMode = DataSourceMode.SIMULATION
        self.sensor_connection: Optional[SensorConnection] = None
        self.simulation_generator: Optional[SimulationGenerator] = None
    
    def set_mode(self, mode: DataSourceMode) -> None:
        """
        Switch between sensor and simulation mode
        
        Args:
            mode: DataSourceMode (SIMULATION or SENSOR)
        """
        self.mode = mode
        logger.info(f"Data source mode set to: {mode.value}")
    
    def set_sensor_connection(self, connection: SensorConnection) -> None:
        """Set sensor connection"""
        self.sensor_connection = connection
        logger.info(f"Sensor connection configured: {connection.device_id}")
    
    def set_simulation_generator(self, generator: SimulationGenerator) -> None:
        """Set simulation generator"""
        self.simulation_generator = generator
        logger.info(f"Simulation generator configured: {generator.device_id}")
    
    def get_data(self) -> Optional[RawSensorData]:
        """
        Get next data point from current source
        
        Returns:
            RawSensorData or None
        """
        if self.mode == DataSourceMode.SENSOR:
            if not self.sensor_connection:
                logger.error("Sensor mode active but no sensor connection configured")
                return None
            return self.sensor_connection.receive_data()
        
        elif self.mode == DataSourceMode.SIMULATION:
            if not self.simulation_generator:
                logger.error("Simulation mode active but no simulation generator configured")
                return None
            return self.simulation_generator.generate_data_point()
        
        return None
    
    def get_connection_status(self) -> ConnectionStatus:
        """
        Get current connection status (for sensor mode)
        
        Returns:
            ConnectionStatus
        """
        if self.mode == DataSourceMode.SENSOR and self.sensor_connection:
            return self.sensor_connection.update_status()
        
        # Simulation mode is always "connected"
        return ConnectionStatus.CONNECTED
    
    def is_available(self) -> bool:
        """
        Check if data source is available
        
        Returns:
            True if data source is ready
        """
        if self.mode == DataSourceMode.SENSOR:
            return (self.sensor_connection is not None and 
                   self.sensor_connection.status == ConnectionStatus.CONNECTED)
        
        elif self.mode == DataSourceMode.SIMULATION:
            return self.simulation_generator is not None
        
        return False
