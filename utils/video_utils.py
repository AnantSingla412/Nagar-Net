"""Video Processing Utilities - Using project data/uploads folder"""

import cv2
import os
import streamlit as st
import shutil
from datetime import datetime
import hashlib

def ensure_upload_directory():
    """Ensure the uploads directory exists"""
    upload_dir = os.path.join("data", "uploads")
    try:
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    except Exception as e:
        st.error(f"Error creating upload directory: {str(e)}")
        return None

def generate_unique_filename(original_filename):
    """Generate a unique filename to avoid conflicts"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    # Clean the filename of special characters
    clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return f"{timestamp}_{clean_name}{ext}"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to data/uploads directory"""
    try:
        # Ensure upload directory exists
        upload_dir = ensure_upload_directory()
        if not upload_dir:
            return None
        
        # Generate unique filename
        unique_filename = generate_unique_filename(uploaded_file.name)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Get file size for logging
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        # Save the file
        uploaded_file.seek(0)  # Reset file pointer
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Verify file was saved correctly
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            st.success(f"✅ File saved: {unique_filename} ({file_size_mb:.1f}MB)")
            return file_path
        else:
            st.error("❌ File was not saved properly")
            return None
            
    except PermissionError:
        st.error("""
        ❌ **Permission Error!** 
        Cannot write to data/uploads directory. 
        Please check folder permissions or run as administrator.
        """)
        return None
    except OSError as e:
        if e.errno == 28:
            st.error("❌ No space left on device")
        else:
            st.error(f"❌ OS Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error saving uploaded file: {str(e)}")
        return None

def get_video_info(video_path):
    """Extract video information"""
    try:
        if not os.path.exists(video_path):
            st.error(f"Video file not found: {video_path}")
            return None
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("Cannot open video file")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # Get file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        return {
            'fps': fps,
            'frame_count': int(frame_count),
            'duration': duration,
            'width': width,
            'height': height,
            'file_size_mb': file_size_mb
        }
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def get_first_frame(video_path):
    """Extract first frame from video"""
    try:
        if not os.path.exists(video_path):
            return None
            
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return frame
        return None
    except Exception as e:
        st.error(f"Error extracting first frame: {str(e)}")
        return None

def list_uploaded_files():
    """List all files in the uploads directory"""
    try:
        upload_dir = os.path.join("data", "uploads")
        if not os.path.exists(upload_dir):
            return []
        
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                files.append({
                    'filename': filename,
                    'path': file_path,
                    'size_mb': file_size,
                    'modified': modified_time
                })
        
        # Sort by modification time (newest first)
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        st.error(f"Error listing uploaded files: {str(e)}")
        return []

def cleanup_old_files(days_old=7):
    """Clean up files older than specified days"""
    try:
        upload_dir = os.path.join("data", "uploads")
        if not os.path.exists(upload_dir):
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
        
        if deleted_count > 0:
            st.info(f"🧹 Cleaned up {deleted_count} old files")
        
        return deleted_count
    except Exception as e:
        st.error(f"Error during cleanup: {str(e)}")
        return 0

def delete_file(file_path):
    """Delete a specific file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"✅ File deleted: {os.path.basename(file_path)}")
            return True
        else:
            st.warning("File not found")
            return False
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False

def get_upload_directory_info():
    """Get information about the uploads directory"""
    try:
        upload_dir = os.path.join("data", "uploads")
        
        if not os.path.exists(upload_dir):
            return {
                'exists': False,
                'total_files': 0,
                'total_size_mb': 0
            }
        
        total_files = 0
        total_size = 0
        
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                total_files += 1
                total_size += os.path.getsize(file_path)
        
        return {
            'exists': True,
            'path': upload_dir,
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'writable': os.access(upload_dir, os.W_OK)
        }
    except Exception as e:
        st.error(f"Error getting directory info: {str(e)}")
        return {'exists': False, 'total_files': 0, 'total_size_mb': 0}