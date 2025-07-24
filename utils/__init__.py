"""Package initialization file"""
# utils/__init__.py
"""
Utilities package for Traffic Analysis Application

This package contains utility functions for:
- ROI (Region of Interest) selection and validation
- Video processing and frame extraction
- Data visualization and chart generation
"""

from .roi_selector import draw_roi_selector, validate_roi_points
from .video_utils import save_uploaded_file, get_video_info, get_first_frame
from .visualization import (
    create_waiting_time_charts,
    create_speed_charts, 
    create_congestion_charts,
    display_metrics
)

__all__ = [
    'draw_roi_selector',
    'validate_roi_points',
    'save_uploaded_file',
    'get_video_info',
    'get_first_frame',
    'create_waiting_time_charts',
    'create_speed_charts',
    'create_congestion_charts',
    'display_metrics'
]

__version__ = "1.0.0"
__author__ = "Traffic Analysis Team"