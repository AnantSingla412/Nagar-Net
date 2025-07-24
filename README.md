# Nagar-Net
# Traffic Analysis Dashboard

A comprehensive Streamlit-based application for analyzing traffic videos using YOLO object detection and DeepSORT tracking.

## Features

- **Waiting Time Analysis**: Track vehicles in a Region of Interest (ROI) and calculate waiting times
- **Speed Analysis**: Measure vehicle speeds within the ROI
- **Congestion Analysis**: Analyze traffic congestion levels and capacity utilization
- **Interactive ROI Selection**: Define custom regions for analysis
- **Real-time Progress Tracking**: Monitor analysis progress with progress bars
- **Data Export**: Download results as CSV files
- **Visualization**: Interactive charts and graphs for data visualization

## Installation

### 1. Clone the repository:
```
git clone <repository-url>
cd traffic_analysis_project
```
### 2. Install dependencies:
```
bashpip install -r requirements.txt
```
### 3. Create necessary directories:
```
bashmkdir -p data/uploads data/outputs
```
##Usage
###Run the Streamlit application:
```
bashstreamlit run app.py
```
