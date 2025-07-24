"""Data Visualization Utilities"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def create_waiting_time_charts(waiting_times_data, avg_waiting_times_data):
    """Create waiting time visualization charts"""
    charts = {}
    
    if waiting_times_data:
        df_waiting = pd.DataFrame(waiting_times_data)
        charts['individual_waiting_times'] = df_waiting
        
    if avg_waiting_times_data:
        df_avg = pd.DataFrame(avg_waiting_times_data)
        charts['average_waiting_times'] = df_avg
        
    return charts

def create_speed_charts(speed_data):
    """Create speed analysis charts"""
    if speed_data:
        df_speeds = pd.DataFrame(speed_data)
        return df_speeds
    return None

def create_congestion_charts(congestion_data):
    """Create congestion analysis charts"""
    if congestion_data:
        df_congestion = pd.DataFrame(congestion_data)
        return df_congestion
    return None

def display_metrics(data, analysis_type):
    """Display key metrics based on analysis type"""
    if analysis_type == "waiting_time" and data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Vehicles Tracked", data.get('total_vehicles', 0))
        with col2:
            st.metric("Frames Processed", data.get('processed_frames', 0))
            
    elif analysis_type == "speed" and data:
        st.metric("Frames Processed", data.get('processed_frames', 0))
        
    elif analysis_type == "congestion" and data:
        if data.get('congestion_data'):
            df = pd.DataFrame(data['congestion_data'])
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_congestion = df['congestion_level'].mean()
                st.metric("Average Congestion Level", f"{avg_congestion:.2f}")
            with col2:
                max_vehicles = df['vehicles'].max()
                st.metric("Peak Vehicle Count", max_vehicles)
            with col3:
                avg_capacity = df['capacity'].mean()
                st.metric("Average Capacity", f"{avg_capacity:.0f}")