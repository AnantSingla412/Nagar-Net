"""ROI Selection Utilities"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def draw_roi_selector(image):
    """Interactive ROI selector using Streamlit"""
    st.subheader("🎯 Define Region of Interest (ROI)")
    
    # Display instructions
    st.info("""
    **Instructions:**
    1. Enter coordinate points for your ROI polygon
    2. You need at least 3 points to form a valid polygon
    3. Points should be in (x, y) format within the image bounds
    4. Use the image below as reference for coordinates
    """)
    
    # Display image for reference
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.set_title("Reference Image - Use this to determine ROI coordinates")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    # ROI point input
    st.subheader("Enter ROI Points")
    num_points = st.number_input("Number of ROI points", min_value=3, max_value=10, value=4)
    
    roi_points = []
    cols = st.columns(2)
    
    for i in range(num_points):
        col_idx = i % 2
        with cols[col_idx]:
            x = st.number_input(f"Point {i+1} - X coordinate", 
                               min_value=0, max_value=image.shape[1], 
                               value=int(image.shape[1] * (0.2 + 0.6 * i / max(num_points-1, 1))),
                               key=f"x_{i}")
            y = st.number_input(f"Point {i+1} - Y coordinate", 
                               min_value=0, max_value=image.shape[0], 
                               value=int(image.shape[0] * (0.3 if i < num_points//2 else 0.7)),
                               key=f"y_{i}")
            roi_points.append((x, y))
    
    # Preview ROI
    if len(roi_points) >= 3:
        preview_img = image.copy()
        pts = np.array(roi_points, np.int32)
        cv2.polylines(preview_img, [pts], True, (0, 255, 0), 3)
        for i, pt in enumerate(roi_points):
            cv2.circle(preview_img, pt, 5, (0, 0, 255), -1)
            cv2.putText(preview_img, str(i+1), (pt[0]+10, pt[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        st.subheader("ROI Preview")
        st.image(cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB), caption="ROI Preview")
        
        return roi_points
    
    return []

def validate_roi_points(roi_points, image_shape):
    """Validate ROI points are within image bounds"""
    height, width = image_shape[:2]
    valid_points = []
    
    for x, y in roi_points:
        if 0 <= x < width and 0 <= y < height:
            valid_points.append((x, y))
        else:
            st.warning(f"Point ({x}, {y}) is outside image bounds")
    
    return valid_points