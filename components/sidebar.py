"""Sidebar Configuration Component"""

import streamlit as st
from config.config import *

def create_sidebar():
    """Create and configure sidebar"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        selected_model = st.selectbox("Select YOLO Model", MODEL_OPTIONS, index=0)
        conf_threshold = st.slider("Confidence Threshold", 0.1, 0.9, DEFAULT_CONF_THRESHOLD, 0.1)
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Waiting Time Analysis", "Speed Analysis", "Congestion Analysis"]
        )
        
        st.markdown("---")
        
        # Additional parameters based on analysis type
        additional_params = {}
        
        if analysis_type == "Waiting Time Analysis":
            additional_params['movement_threshold'] = st.slider(
                "Movement Threshold (pixels)", 1, 20, DEFAULT_MOVEMENT_THRESHOLD
            )
            additional_params['frame_rate'] = st.number_input(
                "Frame Rate", min_value=1, max_value=60, value=DEFAULT_FRAME_RATE
            )
            
        elif analysis_type == "Speed Analysis":
            additional_params['pixels_per_meter'] = st.number_input(
                "Pixels per Meter", min_value=1.0, max_value=50.0, value=DEFAULT_PIXELS_PER_METER
            )
            
        elif analysis_type == "Congestion Analysis":
            additional_params['num_lanes'] = st.number_input(
                "Number of Lanes", min_value=1, max_value=10, value=DEFAULT_NUM_LANES
            )
        
        return {
            'selected_model': selected_model,
            'conf_threshold': conf_threshold,
            'analysis_type': analysis_type,
            **additional_params
        }