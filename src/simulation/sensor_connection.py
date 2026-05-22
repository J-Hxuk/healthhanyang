"""
Sensor Connection Module

Manages communication with physical weight sensor
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from ..data.schema import RawSensorData, ConnectionStatus


logger = logging.getLogger(__name__)


class SensorConnection:
    """Manages physical sensor communication"""
    
    # Connection timeout thresholds
    CONNECTED_THRESHOLD = 30  # seconds
    DISCONNECTED_THRESHOLD = 60  # seconds
    
    def __init__(self, device_id: str, connection_config: dict):
        """
        Initialize sensor connection
        
        Args:
            device_id: Device identifier
            connection_config: Connection configuration (e.g., serial port, IP address)
        """
        self.device_id = device_id
        self.connection_config = connection_config
        self.status = ConnectionStatus.DISCONNECTED
        self.last_received: Optional[datetime] = None
        self.last_weight: Optional[float] = None
        self.connection_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
    
    def connect(self) -> bool:
        """
        Establish connection to physical sensor
        
        Returns:
            True if connection successful
        """
        try:
            # TODO: Implement actual sensor connection logic
            # This would depend on the sensor hardware (serial, TCP/IP, etc.)
            logger.info(f"Connecting to sensor {self.device_id}...")
            
            # Placeholder for actual connection
            self.status = ConnectionStatus.CONNECTED
            self.connection_time = datetime.now()
            self.error_message = None
            
            logger.info(f"Connected to sensor {self.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to sensor {self.device_id}: {e}")
            self.status = ConnectionStatus.ERROR
            self.error_message = str(e)
            return False
    
    def disconnect(self) -> None:
        """Close connection to physical sensor"""
        try:
            # TODO: Implement actual disconnection logic
            logger.info(f"Disconnecting from sensor {self.device_id}...")
            
            self.status = ConnectionStatus.DISCONNECTED
            self.connection_time = None
            
            logger.info(f"Disconnected from sensor {self.device_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from sensor {self.device_id}: {e}")
    
    def receive_data(self) -> Optional[RawSensorData]:
        """
        Receive data from sensor (blocking or timeout)
        
        Returns:
            RawSensorData or None
        """
        try:
            # TODO: Implement actual data reception logic
            # This would read from serial port, TCP socket, etc.
            
            # Placeholder - would normally read from hardware
            logger.debug(f"Receiving data from sensor {self.device_id}...")
            
            # Update last received time
            self.last_received = datetime.now()
            
            # Return None for now (no actual hardware)
            return None
            
        except Exception as e:
            logger.error(f"Error receiving data from sensor {self.device_id}: {e}")
            self.status = ConnectionStatus.ERROR
            self.error_message = str(e)
            return None
    
    def update_status(self) -> ConnectionStatus:
        """
        Update connection status based on last received time
        
        Returns:
            Current ConnectionStatus
        """
        if self.last_received is None:
            # Never received data
            if self.status == ConnectionStatus.CONNECTED:
                # Just connected, waiting for first data
                return self.status
            return ConnectionStatus.DISCONNECTED
        
        time_since_last = datetime.now() - self.last_received
        
        if time_since_last.total_seconds() < self.CONNECTED_THRESHOLD:
            # Recently received data - connected
            if self.status != ConnectionStatus.CONNECTED:
                logger.info(f"Sensor {self.device_id} status: CONNECTED")
                self.status = ConnectionStatus.CONNECTED
                self.error_message = None
        
        elif time_since_last.total_seconds() < self.DISCONNECTED_THRESHOLD:
            # No recent data but within timeout - disconnected
            if self.status != ConnectionStatus.DISCONNECTED:
                logger.warning(f"Sensor {self.device_id} status: DISCONNECTED "
                             f"(no data for {time_since_last.total_seconds():.0f}s)")
                self.status = ConnectionStatus.DISCONNECTED
                self.error_message = f"No data received for {time_since_last.total_seconds():.0f} seconds"
        
        else:
            # Timeout exceeded - error
            if self.status != ConnectionStatus.ERROR:
                logger.error(f"Sensor {self.device_id} status: ERROR "
                           f"(timeout: {time_since_last.total_seconds():.0f}s)")
                self.status = ConnectionStatus.ERROR
                self.error_message = f"Connection timeout ({time_since_last.total_seconds():.0f}s)"
        
        return self.status
    
    def get_device_info(self) -> dict:
        """
        Get sensor device information
        
        Returns:
            Device info dictionary
        """
        return {
            'device_id': self.device_id,
            'status': self.status.value,
            'last_received': self.last_received.isoformat() if self.last_received else None,
            'last_weight': self.last_weight,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'error_message': self.error_message,
            'config': self.connection_config
        }
