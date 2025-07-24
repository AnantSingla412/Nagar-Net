"""Results Display Components"""

import streamlit as st
import pandas as pd
from utils.visualization import display_metrics

def display_waiting_time_results(results):
    """Display waiting time analysis results"""
    if not results:
        st.error("No results to display")
        return
        
    st.success("✅ Waiting time analysis completed!")
    
    # Display metrics
    display_metrics(results, "waiting_time")
    
    # Individual waiting times
    if results['waiting_times']:
        df_waiting = pd.DataFrame(results['waiting_times'])
        st.subheader("📊 Individual Waiting Times")
        st.dataframe(df_waiting)
        
        # Download CSV
        csv = df_waiting.to_csv(index=False)
        st.download_button(
            label="📥 Download Waiting Times CSV",
            data=csv,
            file_name="waiting_times.csv",
            mime="text/csv"
        )
    
    # Average waiting times
    if results['avg_waiting_times']:
        df_avg = pd.DataFrame(results['avg_waiting_times'])
        st.subheader("📈 Average Waiting Times by Minute")
        st.line_chart(df_avg.set_index('minute_mark')['avg_wait_seconds'])
        
        csv_avg = df_avg.to_csv(index=False)
        st.download_button(
            label="📥 Download Average Times CSV",
            data=csv_avg,
            file_name="avg_waiting_times.csv",
            mime="text/csv"
        )

def display_speed_results(results):
    """Display speed analysis results"""
    if not results:
        st.error("No results to display")
        return
        
    st.success("✅ Speed analysis completed!")
    
    display_metrics(results, "speed")
    
    if results['avg_speeds']:
        df_speeds = pd.DataFrame(results['avg_speeds'])
        st.subheader("📊 Average Speeds Over Time")
        st.line_chart(df_speeds.set_index('timestamp')['avg_speed_kmh'])
        
        st.subheader("📈 Speed Data Table")
        st.dataframe(df_speeds)
        
        csv = df_speeds.to_csv(index=False)
        st.download_button(
            label="📥 Download Speed Data CSV",
            data=csv,
            file_name="average_speeds.csv",
            mime="text/csv"
        )

def display_congestion_results(results):
    """Display congestion analysis results"""
    if not results:
        st.error("No results to display")
        return
        
    st.success("✅ Congestion analysis completed!")
    
    display_metrics(results, "congestion")
    
    if results['congestion_data']:
        df_congestion = pd.DataFrame(results['congestion_data'])
        
        # Charts
        st.subheader("📊 Congestion Level Over Time")
        st.line_chart(df_congestion.set_index('time_sec')['congestion_level'])
        
        st.subheader("📈 Vehicle Count Over Time")
        st.line_chart(df_congestion.set_index('time_sec')['vehicles'])
        
        st.subheader("📋 Congestion Data Table")
        st.dataframe(df_congestion)
        
        csv = df_congestion.to_csv(index=False)
        st.download_button(
            label="📥 Download Congestion Data CSV",
            data=csv,
            file_name="congestion_data.csv",
            mime="text/csv"
        )