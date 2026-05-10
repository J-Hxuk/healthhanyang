"""
Event Classification Module

Classifies events into types: cat_visit, cleaning, litter_refill, noise, unknown
"""

import logging
from typing import Tuple

from ..data.schema import Event, EventType
from config.config import get_config


logger = logging.getLogger(__name__)


class EventClassifier:
    """Classifies events based on features"""
    
    def __init__(self):
        self.config = get_config()
    
    def classify(self, event: Event) -> Tuple[EventType, float]:
        """
        Classify event and calculate confidence
        
        Args:
            event: Event to classify
            
        Returns:
            Tuple of (event_type, confidence_score)
        """
        # Check each classification in order of specificity
        
        # 1. Check for noise (very short or very small weight change)
        if self._is_noise(event):
            return EventType.NOISE, 0.9
        
        # 2. Check for cat visit
        if self._is_cat_visit(event):
            confidence = self._calculate_cat_visit_confidence(event)
            return EventType.CAT_VISIT, confidence
        
        # 3. Check for litter refill (baseline increased significantly)
        if self._is_litter_refill(event):
            return EventType.LITTER_REFILL, 0.85
        
        # 4. Check for cleaning (unstable, short, or baseline decreased)
        if self._is_cleaning(event):
            return EventType.CLEANING, 0.8
        
        # 5. Default to unknown
        return EventType.UNKNOWN, 0.5
    
    def _is_noise(self, event: Event) -> bool:
        """Check if event is noise"""
        return (
            event.duration < self.config.noise_duration_threshold or
            event.weight_gain < self.config.noise_weight_threshold
        )
    
    def _is_cat_visit(self, event: Event) -> bool:
        """Check if event matches cat visit pattern"""
        return (
            self.config.cat_min_weight <= event.weight_gain <= self.config.cat_max_weight and
            self.config.min_visit_duration <= event.duration <= self.config.max_visit_duration and
            event.stability_score >= self.config.stability_threshold and
            event.baseline_shift < self.config.max_baseline_shift_for_cat
        )
    
    def _is_litter_refill(self, event: Event) -> bool:
        """Check if event is litter refill"""
        return (
            event.baseline_shift > self.config.baseline_shift_threshold and
            event.baseline_after > event.baseline_before  # Weight increased
        )
    
    def _is_cleaning(self, event: Event) -> bool:
        """Check if event is cleaning"""
        return (
            event.duration < self.config.min_visit_duration or
            event.stability_score < self.config.stability_threshold or
            event.baseline_after < event.baseline_before  # Weight decreased
        )
    
    def _calculate_cat_visit_confidence(self, event: Event) -> float:
        """
        Calculate confidence score for cat visit classification
        
        Higher confidence when:
        - Weight gain is in middle of cat weight range
        - Duration is typical (not too short or long)
        - Stability is high
        - Baseline shift is minimal
        
        Returns:
            Confidence score between 0 and 1
        """
        scores = []
        
        # Weight gain score (peak at middle of range)
        weight_range = self.config.cat_max_weight - self.config.cat_min_weight
        weight_center = (self.config.cat_max_weight + self.config.cat_min_weight) / 2
        weight_deviation = abs(event.weight_gain - weight_center) / (weight_range / 2)
        weight_score = max(0, 1 - weight_deviation)
        scores.append(weight_score)
        
        # Duration score (prefer middle range)
        duration_range = self.config.max_visit_duration - self.config.min_visit_duration
        duration_center = (self.config.max_visit_duration + self.config.min_visit_duration) / 2
        duration_deviation = abs(event.duration - duration_center) / (duration_range / 2)
        duration_score = max(0, 1 - duration_deviation)
        scores.append(duration_score)
        
        # Stability score (already 0-1)
        scores.append(event.stability_score)
        
        # Baseline shift score (lower is better)
        baseline_shift_score = max(0, 1 - (event.baseline_shift / self.config.max_baseline_shift_for_cat))
        scores.append(baseline_shift_score)
        
        # Average all scores
        confidence = sum(scores) / len(scores)
        
        # Ensure in valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
