"""
Configuration Management for Cat Health Copilot

Loads and manages system configuration parameters from thresholds.json
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for system thresholds and parameters"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to thresholds.json file. If None, uses default location.
        """
        if config_path is None:
            # Default to config/thresholds.json relative to this file
            config_dir = Path(__file__).parent
            config_path = config_dir / 'thresholds.json'
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Configuration section (e.g., 'preprocessing', 'classification')
            key: Configuration key within section
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value (runtime only, not persisted)
        
        Args:
            section: Configuration section
            key: Configuration key
            value: New value
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # Preprocessing parameters
    @property
    def moving_average_window(self) -> int:
        return self.get('preprocessing', 'moving_average_window', 5)
    
    @property
    def noise_threshold(self) -> float:
        return self.get('preprocessing', 'noise_threshold', 0.05)
    
    @property
    def outlier_threshold(self) -> float:
        return self.get('preprocessing', 'outlier_threshold', 3.0)
    
    # Event detection parameters
    @property
    def weight_change_threshold(self) -> float:
        return self.get('event_detection', 'weight_change_threshold', 0.5)
    
    @property
    def min_event_duration(self) -> float:
        return self.get('event_detection', 'min_event_duration', 2.0)
    
    @property
    def max_event_duration(self) -> float:
        return self.get('event_detection', 'max_event_duration', 600.0)
    
    @property
    def stability_duration(self) -> float:
        return self.get('event_detection', 'stability_duration', 5.0)
    
    # Classification parameters
    @property
    def cat_min_weight(self) -> float:
        return self.get('classification', 'cat_min_weight', 1.5)
    
    @property
    def cat_max_weight(self) -> float:
        return self.get('classification', 'cat_max_weight', 10.0)
    
    @property
    def min_visit_duration(self) -> float:
        return self.get('classification', 'min_visit_duration', 5.0)
    
    @property
    def max_visit_duration(self) -> float:
        return self.get('classification', 'max_visit_duration', 300.0)
    
    @property
    def baseline_shift_threshold(self) -> float:
        return self.get('classification', 'baseline_shift_threshold', 0.2)
    
    @property
    def stability_threshold(self) -> float:
        return self.get('classification', 'stability_threshold', 0.6)
    
    @property
    def max_baseline_shift_for_cat(self) -> float:
        return self.get('classification', 'max_baseline_shift_for_cat', 0.2)
    
    @property
    def noise_duration_threshold(self) -> float:
        return self.get('classification', 'noise_duration_threshold', 2.0)
    
    @property
    def noise_weight_threshold(self) -> float:
        return self.get('classification', 'noise_weight_threshold', 0.3)
    
    # Identification parameters
    @property
    def unknown_confidence_threshold(self) -> float:
        return self.get('identification', 'unknown_confidence_threshold', 1.0)
    
    # Health analysis parameters
    @property
    def warning_threshold(self) -> float:
        return self.get('health_analysis', 'warning_threshold', 0.5)
    
    @property
    def critical_threshold(self) -> float:
        return self.get('health_analysis', 'critical_threshold', 1.0)
    
    @property
    def trend_window_days(self) -> int:
        return self.get('health_analysis', 'trend_window_days', 7)
    
    # Alert parameters
    @property
    def suppression_window_hours(self) -> int:
        return self.get('alerts', 'suppression_window_hours', 24)


# Global configuration instance
_config_instance = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """Reload global configuration from file"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()
