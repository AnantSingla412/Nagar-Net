"""Configuration settings for the Traffic Analysis Application"""

# Model Configuration
MODEL_OPTIONS = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]
DEFAULT_MODEL = "yolov8n.pt"
DEFAULT_CONF_THRESHOLD = 0.5
DEFAULT_IOU_THRESHOLD = 0.3

# Tracker Configuration
DEFAULT_MAX_AGE = 30

# Analysis Parameters
DEFAULT_MOVEMENT_THRESHOLD = 5
DEFAULT_FRAME_RATE = 30
DEFAULT_PIXELS_PER_METER = 8.0
DEFAULT_NUM_LANES = 2

# Vehicle Classes (COCO dataset)
VEHICLE_CLASSES = {
    'car': 2,
    'motorcycle': 3,
    'bus': 5,
    'truck': 7
}

# Speed Analysis
MIN_REASONABLE_SPEED = 1  # km/h
MAX_REASONABLE_SPEED = 120  # km/h

# File Upload
SUPPORTED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv']
MAX_UPLOAD_SIZE = 200  # MB

# UI Configuration
PAGE_TITLE = "Traffic Analysis Dashboard"
PAGE_ICON = "🚗"