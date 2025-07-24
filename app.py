"""Main Streamlit Application for Traffic Analysis"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import tempfile
import os

# Import custom modules
from config.config import *
from models.traffic_analyzer import TrafficAnalyzer
from utils.roi_selector import draw_roi_selector
from utils.video_utils import save_uploaded_file, get_video_info, get_first_frame
from components.sidebar import create_sidebar
from components.results_display import (
    display_waiting_time_results, 
    display_speed_results, 
    display_congestion_results
)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS styles"""
    with open('static/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Try to load CSS, fallback to inline styles if file doesn't exist
try:
    load_css()
except FileNotFoundError:
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stSelectbox > div > div > select {
            background-color: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)

def create_file_management_sidebar():
    """Create file management section in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("📁 File Management")
        
        # Show upload directory info
        dir_info = get_upload_directory_info()
        if dir_info['exists']:
            st.info(f"""
            **Upload Directory:**
            - Files: {dir_info['total_files']}
            - Total Size: {dir_info['total_size_mb']:.1f} MB
            - Writable: {'✅' if dir_info['writable'] else '❌'}
            """)
        
        # Cleanup options
        if st.button("🧹 Clean Old Files (7+ days)"):
            cleanup_old_files(7)
            st.rerun()
        
        # List recent files
        uploaded_files = list_uploaded_files()
        if uploaded_files:
            st.subheader("📋 Recent Uploads")
            for file_info in uploaded_files[:3]:  # Show last 3 files
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{file_info['filename'][:20]}...")
                    st.caption(f"{file_info['size_mb']:.1f}MB")
                with col2:
                    if st.button("🗑️", key=f"del_{file_info['filename']}", 
                                help="Delete file"):
                        delete_file(file_info['path'])
                        st.rerun()

# Updated main content area for file upload
def create_upload_section():
    """Create the video upload section"""
    st.header("📹 Video Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a traffic video for analysis"
    )
    
    if uploaded_file is not None:
        # Show file details
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.info(f"""
        **Selected File:**
        - Name: {uploaded_file.name}
        - Size: {file_size_mb:.2f} MB
        - Type: {uploaded_file.type}
        """)
        
        # Check file size (optional limit)
        max_size_mb = 500  # Adjust as needed
        if file_size_mb > max_size_mb:
            st.error(f"❌ File too large: {file_size_mb:.1f}MB. Maximum allowed: {max_size_mb}MB")
        else:
            # Save file button
            if st.button("💾 Save Video", type="primary"):
                with st.spinner("Saving video file..."):
                    saved_path = save_uploaded_file(uploaded_file)
                    
                    if saved_path:
                        # Store in session state
                        st.session_state.video_path = saved_path
                        
                        # Get video info and first frame
                        video_info = get_video_info(saved_path)
                        first_frame = get_first_frame(saved_path)
                        
                        if video_info and first_frame is not None:
                            st.session_state.first_frame = first_frame
                            st.session_state.video_info = video_info
                            
                            # Display video information
                            st.success("✅ Video processed successfully!")
                            st.json(video_info)
                        else:
                            st.error("❌ Failed to process video file")
    
    # Show current loaded video
    if 'video_path' in st.session_state:
        st.success(f"✅ Video loaded: {os.path.basename(st.session_state.video_path)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Load Different Video"):
                # Clear current video from session state
                for key in ['video_path', 'first_frame', 'video_info']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Current Video"):
                if delete_file(st.session_state.video_path):
                    # Clear from session state
                    for key in ['video_path', 'first_frame', 'video_info']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

# Updated main function
def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🚗 Traffic Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize analyzer in session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = TrafficAnalyzer()
    
    # Create sidebar and get configuration
    config = create_sidebar()
    
    # Add file management to sidebar
    create_file_management_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        create_upload_section()
    
    with col2:
        if 'first_frame' in st.session_state:
            # ROI Selection
            roi_points = draw_roi_selector(st.session_state.first_frame)
            
            if len(roi_points) >= 3:
                st.success(f"✅ ROI defined with {len(roi_points)} points")
                
                # Start Analysis Button
                if st.button("🚀 Start Analysis", type="primary"):
                    with st.spinner("Loading model and initializing tracker..."):
                        # Initialize model and tracker
                        model_loaded = st.session_state.analyzer.load_model(
                            config['selected_model'], 
                            config['conf_threshold']
                        )
                        tracker_loaded = st.session_state.analyzer.initialize_tracker()
                        
                        if model_loaded and tracker_loaded:
                            st.success("✅ Model and tracker initialized successfully!")
                            
                            # Run analysis based on selected type
                            analysis_type = config['analysis_type']
                            
                            if analysis_type == "Waiting Time Analysis":
                                with st.spinner("Analyzing waiting times..."):
                                    results = st.session_state.analyzer.analyze_waiting_times(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['movement_threshold'],
                                        config['frame_rate']
                                    )
                                    display_waiting_time_results(results)
                            
                            elif analysis_type == "Speed Analysis":
                                with st.spinner("Analyzing vehicle speeds..."):
                                    results = st.session_state.analyzer.analyze_speed(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['pixels_per_meter']
                                    )
                                    display_speed_results(results)
                            
                            elif analysis_type == "Congestion Analysis":
                                with st.spinner("Analyzing traffic congestion..."):
                                    results = st.session_state.analyzer.analyze_congestion(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['num_lanes']
                                    )
                                    display_congestion_results(results)
                        else:
                            st.error("❌ Failed to initialize model or tracker")
            else:
                st.warning("⚠️ Please define a ROI with at least 3 points to proceed")
        else:
            st.info("👆 Please upload and save a video file to get started")
def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🚗 Traffic Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize analyzer in session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = TrafficAnalyzer()
    
    # Create sidebar and get configuration
    config = create_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📹 Video Upload")
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=SUPPORTED_VIDEO_FORMATS,
            help="Upload a traffic video for analysis"
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            temp_path = save_uploaded_file(uploaded_file)
            
            if temp_path:
                st.success(f"✅ Video uploaded: {uploaded_file.name}")
                
                # Get video information
                video_info = get_video_info(temp_path)
                first_frame = get_first_frame(temp_path)
                
                if video_info and first_frame is not None:
                    st.session_state.video_path = temp_path
                    st.session_state.first_frame = first_frame
                    
                    # Display video info
                    st.info(f"""
                    **Video Information:**
                    - Duration: {video_info['duration']:.2f} seconds
                    - FPS: {video_info['fps']:.2f}
                    - Total Frames: {video_info['frame_count']}
                    - Resolution: {video_info['width']}x{video_info['height']}
                    """)
                else:
                    st.error("❌ Failed to process video file")
    
    with col2:
        if 'first_frame' in st.session_state:
            # ROI Selection
            roi_points = draw_roi_selector(st.session_state.first_frame)
            
            if len(roi_points) >= 3:
                st.success(f"✅ ROI defined with {len(roi_points)} points")
                
                # Start Analysis Button
                if st.button("🚀 Start Analysis", type="primary"):
                    with st.spinner("Loading model and initializing tracker..."):
                        # Initialize model and tracker
                        model_loaded = st.session_state.analyzer.load_model(
                            config['selected_model'], 
                            config['conf_threshold']
                        )
                        tracker_loaded = st.session_state.analyzer.initialize_tracker()
                        
                        if model_loaded and tracker_loaded:
                            st.success("✅ Model and tracker initialized successfully!")
                            
                            # Run analysis based on selected type
                            analysis_type = config['analysis_type']
                            
                            if analysis_type == "Waiting Time Analysis":
                                with st.spinner("Analyzing waiting times..."):
                                    results = st.session_state.analyzer.analyze_waiting_times(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['movement_threshold'],
                                        config['frame_rate']
                                    )
                                    display_waiting_time_results(results)
                            
                            elif analysis_type == "Speed Analysis":
                                with st.spinner("Analyzing vehicle speeds..."):
                                    results = st.session_state.analyzer.analyze_speed(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['pixels_per_meter']
                                    )
                                    display_speed_results(results)
                            
                            elif analysis_type == "Congestion Analysis":
                                with st.spinner("Analyzing traffic congestion..."):
                                    results = st.session_state.analyzer.analyze_congestion(
                                        st.session_state.video_path,
                                        roi_points,
                                        config['num_lanes']
                                    )
                                    display_congestion_results(results)
                        else:
                            st.error("❌ Failed to initialize model or tracker")
            else:
                st.warning("⚠️ Please define a ROI with at least 3 points to proceed")
        else:
            st.info("👆 Please upload a video file to get started")

if __name__ == "__main__":
    main()