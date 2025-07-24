"""Core Traffic Analysis Logic"""

import cv2
import numpy as np
import time
import math
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from matplotlib.path import Path
import streamlit as st

class TrafficAnalyzer:
    def __init__(self):
        self.model = None
        self.tracker = None
        self.roi_points = []
        self.roi_path = None
        
    def load_model(self, model_name="yolov8n.pt", conf_threshold=0.5):
        """Load YOLO model with specified parameters"""
        try:
            self.model = YOLO(model_name)
            self.model.conf = conf_threshold
            self.model.iou = 0.3
            self.model.agnostic = True
            return True
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def initialize_tracker(self, max_age=30):
        """Initialize DeepSORT tracker"""
        try:
            self.tracker = DeepSort(max_age=max_age)
            return True
        except Exception as e:
            st.error(f"Error initializing tracker: {str(e)}")
            return False
    
    def set_roi_from_coordinates(self, points):
        """Set ROI from list of coordinate points"""
        self.roi_points = points
        if len(points) >= 3:
            self.roi_path = Path(np.array(points))
            return True
        return False
    
    def analyze_waiting_times(self, video_path, roi_points, movement_threshold=5, frame_rate=30):
        """Analyze vehicle waiting times"""
        results = {
            'waiting_times': [],
            'avg_waiting_times': [],
            'processed_frames': 0,
            'total_vehicles': 0
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
                
            self.set_roi_from_coordinates(roi_points)
            
            # Initialize tracking variables
            entry_positions = {}
            wait_timers = {}
            exit_records = []
            frame_idx = 0
            centroid_history = {}
            already_logged = set()
            latest_tracks = []
            
            # Progress bar
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_idx += 1
                progress = frame_idx / total_frames
                progress_bar.progress(progress)
                status_text.text(f"Processing frame {frame_idx}/{total_frames}")
                
                if frame_idx % frame_rate == 0:
                    # Run YOLO detection
                    yolo_results = self.model(frame)
                    dets = []
                    
                    for r in yolo_results:
                        for b in r.boxes:
                            if int(b.cls[0]) != 2:  # Only cars
                                continue
                            x1, y1, x2, y2 = map(int, b.xyxy[0])
                            dets.append(([x1, y1, x2 - x1, y2 - y1], float(b.conf[0])))
                    
                    # Update tracker
                    latest_tracks = self.tracker.update_tracks(dets, frame=frame)
                    current_second = frame_idx // frame_rate
                    
                    for tr in latest_tracks:
                        if not tr.is_confirmed():
                            continue
                            
                        tid = tr.track_id
                        x1, y1, x2, y2 = map(int, tr.to_ltrb())
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        center = (cx, cy)
                        
                        if self.roi_path.contains_point(center):
                            if tid not in centroid_history:
                                centroid_history[tid] = {}
                            centroid_history[tid][current_second] = center
                            
                            if tid in wait_timers:
                                prev = centroid_history[tid].get(current_second - 1)
                                if prev:
                                    dist = ((cx - prev[0])**2 + (cy - prev[1])**2)**0.5
                                    if dist < movement_threshold:
                                        wait_timers[tid] += 1
                                    else:
                                        if tid not in already_logged:
                                            wt = wait_timers.pop(tid, 0)
                                            if wt > 0:
                                                results['waiting_times'].append({
                                                    'timestamp': self.format_timestamp(frame_idx, frame_rate),
                                                    'track_id': tid,
                                                    'wait_seconds': wt
                                                })
                                                exit_records.append(wt)
                                                already_logged.add(tid)
                                else:
                                    wait_timers[tid] += 1
                            else:
                                wait_timers[tid] = 1
                        elif tid in wait_timers and tid not in already_logged:
                            wt = wait_timers.pop(tid, 0)
                            if wt > 0:
                                results['waiting_times'].append({
                                    'timestamp': self.format_timestamp(frame_idx, frame_rate),
                                    'track_id': tid,
                                    'wait_seconds': wt
                                })
                                exit_records.append(wt)
                                already_logged.add(tid)
                
                # Calculate averages every minute
                if frame_idx % (frame_rate * 60) == 0:
                    if exit_records:
                        avg = sum(exit_records) / len(exit_records)
                        results['avg_waiting_times'].append({
                            'minute_mark': self.format_timestamp(frame_idx, frame_rate),
                            'avg_wait_seconds': round(avg, 2),
                            'vehicle_count': len(exit_records)
                        })
                        exit_records.clear()
            
            # Handle remaining vehicles
            for tid, wt in wait_timers.items():
                if tid not in already_logged:
                    results['waiting_times'].append({
                        'timestamp': self.format_timestamp(frame_idx, frame_rate),
                        'track_id': tid,
                        'wait_seconds': wt
                    })
            
            results['processed_frames'] = frame_idx
            results['total_vehicles'] = len(already_logged)
            
            cap.release()
            progress_bar.empty()
            status_text.empty()
            
            return results
            
        except Exception as e:
            st.error(f"Error in waiting time analysis: {str(e)}")
            return None
    
    def analyze_speed(self, video_path, roi_points, pixels_per_meter=8):
        """Analyze vehicle speeds"""
        results = {
            'speed_data': [],
            'avg_speeds': [],
            'processed_frames': 0
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            vehicle_history = {}
            vehicle_speeds = {}
            interval_counter = 1
            log_interval = 2
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_idx += 1
                progress = frame_idx / total_frames
                progress_bar.progress(progress)
                status_text.text(f"Processing frame {frame_idx}/{total_frames}")
                
                # Run detection
                detections = []
                yolo_results = self.model(frame)[0]
                boxes = yolo_results.boxes
                
                if boxes is not None and boxes.xyxy is not None:
                    vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
                    
                    for i in range(len(boxes)):
                        cls_id = int(boxes.cls[i])
                        if cls_id in vehicle_classes:
                            x1, y1, x2, y2 = map(int, boxes.xyxy[i])
                            conf = float(boxes.conf[i])
                            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "vehicle"))
                
                # Update tracker
                tracks = self.tracker.update_tracks(detections, frame=frame)
                frame_speeds = []
                
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                        
                    track_id = track.track_id
                    l, t, w, h = map(int, track.to_ltrb())
                    x1, y1, x2, y2 = l, t, l + w, t + h
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    
                    # Check if inside ROI
                    if len(roi_points) > 2:
                        if cv2.pointPolygonTest(np.array(roi_points), (cx, cy), False) < 0:
                            continue
                    
                    if track_id not in vehicle_history:
                        vehicle_history[track_id] = []
                    vehicle_history[track_id].append((cx, cy))
                    
                    # Calculate speed if we have enough history
                    if len(vehicle_history[track_id]) >= 2:
                        x_prev, y_prev = vehicle_history[track_id][-2]
                        dist = math.hypot(cx - x_prev, cy - y_prev)
                        px_per_sec = dist * fps
                        meters_per_sec = px_per_sec / pixels_per_meter
                        kmph = meters_per_sec * 3.6
                        
                        if 1 < kmph < 120:  # Reasonable speed range
                            vehicle_speeds[track_id] = kmph
                            frame_speeds.append(kmph)
                
                # Log data at intervals
                timestamp = frame_idx / fps
                avg_speed_kmph = sum(frame_speeds) / len(frame_speeds) if frame_speeds else 0
                
                if timestamp >= interval_counter * log_interval:
                    results['avg_speeds'].append({
                        'timestamp': f"{interval_counter * log_interval:.2f}",
                        'avg_speed_kmh': round(avg_speed_kmph, 2),
                        'vehicle_count': len(frame_speeds)
                    })
                    interval_counter += 1
            
            results['processed_frames'] = frame_idx
            cap.release()
            progress_bar.empty()
            status_text.empty()
            
            return results
            
        except Exception as e:
            st.error(f"Error in speed analysis: {str(e)}")
            return None
    
    def analyze_congestion(self, video_path, roi_points, num_lanes):
        """Analyze traffic congestion"""
        results = {
            'congestion_data': [],
            'processed_frames': 0
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = int(fps)
            
            # Create mask from ROI
            ret, first_frame = cap.read()
            if not ret:
                return None
                
            height, width = first_frame.shape[:2]
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(roi_points)], 1)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            frame_number = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                progress = frame_number / total_frames
                progress_bar.progress(progress)
                status_text.text(f"Processing frame {frame_number}/{total_frames}")
                
                if frame_number % frame_interval == 0:
                    time_stamp = round(frame_number / fps, 2)
                    yolo_results = self.model(frame, verbose=False)[0]
                    vehicle_boxes = []
                    
                    for r in yolo_results.boxes:
                        cls_id = int(r.cls[0])
                        cls_name = self.model.names[cls_id]
                        
                        if cls_name not in {'car', 'motorcycle', 'bus', 'truck'}:
                            continue
                            
                        x1, y1, x2, y2 = map(int, r.xyxy[0])
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        
                        if 0 <= cx < width and 0 <= cy < height and mask[cy, cx] == 1:
                            vehicle_boxes.append((x1, y1, x2, y2))
                    
                    total_vehicles = len(vehicle_boxes)
                    
                    # Calculate congestion using area-based approach
                    vehicle_areas = [(x2 - x1) * (y2 - y1) for (x1, y1, x2, y2) in vehicle_boxes]
                    avg_vehicle_area = int(np.mean(vehicle_areas)) if vehicle_areas else 3600
                    avg_vehicle_area = max(avg_vehicle_area, 1)
                    
                    visible_area_pixels = np.count_nonzero(mask)
                    lane_correction = 0.95
                    dynamic_capacity = int((lane_correction * visible_area_pixels) / avg_vehicle_area)
                    
                    congestion_level = min(total_vehicles / max(dynamic_capacity, 1), 1.5)
                    
                    results['congestion_data'].append({
                        'frame': frame_number,
                        'time_sec': time_stamp,
                        'vehicles': total_vehicles,
                        'lanes': num_lanes,
                        'capacity': dynamic_capacity,
                        'congestion_level': round(congestion_level, 2)
                    })
                
                frame_number += 1
            
            results['processed_frames'] = frame_number
            cap.release()
            progress_bar.empty()
            status_text.empty()
            
            return results
            
        except Exception as e:
            st.error(f"Error in congestion analysis: {str(e)}")
            return None
    
    def format_timestamp(self, frame_idx, frame_rate):
        """Format frame index to timestamp"""
        seconds = frame_idx // frame_rate
        return time.strftime('%H:%M:%S', time.gmtime(seconds))