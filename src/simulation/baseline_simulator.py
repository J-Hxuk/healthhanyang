"""
Baseline Simulator Module

Simulates realistic baseline weight fluctuations during long-term simulation
"""

import random
import logging
from typing import Optional

from ..preprocessing.baseline import BaselineManager


logger = logging.getLogger(__name__)


class BaselineSimulator:
    """Simulates realistic baseline weight fluctuations"""
    
    def __init__(self, baseline_manager: BaselineManager):
        """
        Initialize baseline simulator
        
        Args:
            baseline_manager: BaselineManager instance
        """
        self.baseline_manager = baseline_manager
        
        # Baseline constraints
        self.min_baseline = 1.0  # kg
        self.max_baseline = 5.0  # kg
        self.refill_threshold = 1.5  # kg
        self.cleaning_threshold = 4.5  # kg
    
    def apply_urination_effect(self) -> float:
        """
        Increase baseline by 50-100g (litter clumping)
        
        Returns:
            New baseline weight
        """
        increase = random.uniform(0.050, 0.100)  # 50-100g
        current = self.baseline_manager.get_current_baseline()
        new_baseline = current + increase
        
        # Ensure within valid range
        new_baseline = min(new_baseline, self.max_baseline)
        
        self.baseline_manager.update_baseline(new_baseline, "urination")
        logger.debug(f"Urination effect: +{increase*1000:.0f}g (new: {new_baseline:.3f}kg)")
        
        return new_baseline
    
    def apply_defecation_effect(self) -> float:
        """
        Decrease baseline by 100-200g (waste removal)
        
        Returns:
            New baseline weight
        """
        decrease = random.uniform(0.100, 0.200)  # 100-200g
        current = self.baseline_manager.get_current_baseline()
        new_baseline = current - decrease
        
        # Ensure within valid range
        new_baseline = max(new_baseline, self.min_baseline)
        
        self.baseline_manager.update_baseline(new_baseline, "defecation")
        logger.debug(f"Defecation effect: -{decrease*1000:.0f}g (new: {new_baseline:.3f}kg)")
        
        return new_baseline
    
    def apply_cleaning_effect(self) -> float:
        """
        Decrease baseline by 200-400g (clump removal)
        
        Returns:
            New baseline weight
        """
        decrease = random.uniform(0.200, 0.400)  # 200-400g
        current = self.baseline_manager.get_current_baseline()
        new_baseline = current - decrease
        
        # Ensure within valid range
        new_baseline = max(new_baseline, self.min_baseline)
        
        self.baseline_manager.update_baseline(new_baseline, "cleaning")
        logger.info(f"Cleaning effect: -{decrease*1000:.0f}g (new: {new_baseline:.3f}kg)")
        
        return new_baseline
    
    def apply_refill_effect(self) -> float:
        """
        Increase baseline by 500-1000g (litter refill)
        
        Returns:
            New baseline weight
        """
        increase = random.uniform(0.500, 1.000)  # 500-1000g
        current = self.baseline_manager.get_current_baseline()
        new_baseline = current + increase
        
        # Ensure within valid range
        new_baseline = min(new_baseline, self.max_baseline)
        
        self.baseline_manager.update_baseline(new_baseline, "litter_refill")
        logger.info(f"Refill effect: +{increase*1000:.0f}g (new: {new_baseline:.3f}kg)")
        
        return new_baseline
    
    def check_auto_maintenance(self) -> Optional[str]:
        """
        Check if automatic maintenance event needed
        
        Returns:
            Event type ("refill" or "cleaning") or None
        """
        current = self.baseline_manager.get_current_baseline()
        
        if current <= self.refill_threshold:
            logger.info(f"Auto-maintenance triggered: refill (baseline: {current:.3f}kg <= {self.refill_threshold}kg)")
            return "refill"
        
        elif current >= self.cleaning_threshold:
            logger.info(f"Auto-maintenance triggered: cleaning (baseline: {current:.3f}kg >= {self.cleaning_threshold}kg)")
            return "cleaning"
        
        return None
    
    def ensure_valid_range(self) -> None:
        """Ensure baseline stays within valid range"""
        current = self.baseline_manager.get_current_baseline()
        
        if current < self.min_baseline:
            logger.warning(f"Baseline below minimum ({current:.3f}kg < {self.min_baseline}kg), adjusting")
            self.baseline_manager.update_baseline(self.min_baseline, "auto_adjust")
        
        elif current > self.max_baseline:
            logger.warning(f"Baseline above maximum ({current:.3f}kg > {self.max_baseline}kg), adjusting")
            self.baseline_manager.update_baseline(self.max_baseline, "auto_adjust")
