"""
Simulation Generator Module

Generates simulated sensor data points on demand
"""

import uuid
import random
import logging
from datetime import datetime
from typing import Optional

from ..data.schema import RawSensorData


logger = logging.getLogger(__name__)


class SimulationGenerator:
    """Generates simulated sensor data on demand"""
    
    # Noise parameters
    NOISE_STDDEV = 0.005  # kg (5g standard deviation)
    
    def __init__(self, device_id: str):
        """
        Initialize simulation generator
        
        Args:
            device_id: Device identifier for generated data
        """
        self.device_id = device_id
        self.current_weight = 0.0
        self.baseline_weight = 2.5  # kg
        self.cat_on_pad = False
        self.event_start_time: Optional[datetime] = None
    
    def set_baseline(self, weight: float) -> None:
        """
        Set current baseline weight
        
        Args:
            weight: Baseline weight in kg
        """
        self.baseline_weight = weight
        if not self.cat_on_pad:
            self.current_weight = weight
        logger.debug(f"Baseline weight set to {weight:.3f}kg")
    
    def simulate_cat_entry(self, cat_weight: float) -> None:
        """
        Simulate cat stepping onto pad
        
        Args:
            cat_weight: Cat weight in kg
        """
        self.cat_on_pad = True
        self.current_weight = self.baseline_weight + cat_weight
        self.event_start_time = datetime.now()
        logger.debug(f"Cat entry simulated: {cat_weight:.3f}kg (total: {self.current_weight:.3f}kg)")
    
    def simulate_cat_exit(self) -> None:
        """Simulate cat leaving pad"""
        self.cat_on_pad = False
        self.current_weight = self.baseline_weight
        self.event_start_time = None
        logger.debug(f"Cat exit simulated (baseline: {self.baseline_weight:.3f}kg)")
    
    def add_weight_variation(self, delta: float) -> None:
        """
        Add weight variation (cat movement)
        
        Args:
            delta: Weight change in kg
        """
        self.current_weight += delta
        logger.debug(f"Weight variation: {delta:+.3f}kg (new: {self.current_weight:.3f}kg)")
    
    def generate_data_point(self) -> RawSensorData:
        """
        Generate single sensor data point at current state
        
        Returns:
            RawSensorData with realistic noise
        """
        # Add realistic noise
        noise = random.gauss(0, self.NOISE_STDDEV)
        noisy_weight = max(0, self.current_weight + noise)
        
        # Distribute weight across 4 load cells (simplified)
        # In reality, distribution depends on cat position
        base_per_cell = noisy_weight / 4.0
        cell_variation = self.NOISE_STDDEV * 2
        
        loadcell_1 = max(0, base_per_cell + random.gauss(0, cell_variation))
        loadcell_2 = max(0, base_per_cell + random.gauss(0, cell_variation))
        loadcell_3 = max(0, base_per_cell + random.gauss(0, cell_variation))
        loadcell_4 = max(0, base_per_cell + random.gauss(0, cell_variation))
        
        # Normalize to match total weight
        total_cells = loadcell_1 + loadcell_2 + loadcell_3 + loadcell_4
        if total_cells > 0:
            scale_factor = noisy_weight / total_cells
            loadcell_1 *= scale_factor
            loadcell_2 *= scale_factor
            loadcell_3 *= scale_factor
            loadcell_4 *= scale_factor
        
        # Create data point
        data = RawSensorData(
            id=str(uuid.uuid4()),
            device_id=self.device_id,
            timestamp=int(datetime.now().timestamp() * 1000),  # milliseconds
            received_at=datetime.now(),
            loadcell_1=loadcell_1,
            loadcell_2=loadcell_2,
            loadcell_3=loadcell_3,
            loadcell_4=loadcell_4,
            total_weight=noisy_weight
        )
        
        return data
