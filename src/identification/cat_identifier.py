"""
Cat Identification Module

Identifies which cat used the litter box based on weight
"""

import logging
from typing import List, Tuple, Optional

from ..data.schema import Event, CatProfile
from config.config import get_config


logger = logging.getLogger(__name__)


class CatIdentifier:
    """Identifies cats based on measured weight"""
    
    def __init__(self):
        self.config = get_config()
    
    def identify(self, event: Event, profiles: List[CatProfile]) -> Tuple[Optional[str], float]:
        """
        Identify which cat used the litter box
        
        Args:
            event: Cat visit event
            profiles: List of registered cat profiles
            
        Returns:
            Tuple of (cat_id, confidence_score). cat_id is None if unknown.
        """
        if not profiles:
            logger.warning("No cat profiles registered")
            return None, 0.0
        
        # Calculate measured cat weight
        measured_weight = self.calculate_measured_weight(event)
        
        # Find closest matching cat
        cat_id, weight_diff = self.find_closest_match(measured_weight, profiles)
        
        # Check if difference exceeds unknown threshold
        if weight_diff > self.config.unknown_confidence_threshold:
            logger.info(f"Weight difference ({weight_diff:.3f}kg) exceeds threshold, marking as unknown")
            return None, 0.0
        
        # Calculate confidence
        confidence = self.calculate_confidence(weight_diff)
        
        logger.info(f"Identified cat: {cat_id}, measured={measured_weight:.3f}kg, diff={weight_diff:.3f}kg, confidence={confidence:.2f}")
        
        return cat_id, confidence
    
    def calculate_measured_weight(self, event: Event) -> float:
        """
        Calculate cat weight from event
        
        Args:
            event: Cat visit event
            
        Returns:
            Measured cat weight in kg
        """
        return event.avg_weight - event.baseline_before
    
    def find_closest_match(self, measured_weight: float, profiles: List[CatProfile]) -> Tuple[str, float]:
        """
        Find cat profile with closest matching weight
        
        Args:
            measured_weight: Measured cat weight
            profiles: List of cat profiles
            
        Returns:
            Tuple of (cat_id, weight_difference)
        """
        best_cat_id = None
        best_diff = float('inf')
        
        for profile in profiles:
            diff = abs(measured_weight - profile.baseline_weight)
            if diff < best_diff:
                best_diff = diff
                best_cat_id = profile.cat_id
        
        return best_cat_id, best_diff
    
    def calculate_confidence(self, weight_diff: float) -> float:
        """
        Calculate identification confidence based on weight difference
        
        Smaller difference = higher confidence
        
        Args:
            weight_diff: Absolute weight difference in kg
            
        Returns:
            Confidence score between 0 and 1
        """
        # Use exponential decay: confidence = exp(-diff / scale)
        import math
        scale = 0.5  # kg - scale factor for confidence decay
        confidence = math.exp(-weight_diff / scale)
        
        # Ensure in valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
