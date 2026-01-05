#!/usr/bin/env python3
"""
Flask Web API for ESP32-CAM Detection
Serves stream and detection status to React frontend
"""

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import requests
import time
import cv2
import numpy as np
from threading import Lock
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Shared state (updated by your Python detection script)
detection_state = {
    "humanDetected": False,
    "label": "",
    "confidence": 0.0,
    "track_id": 0,
    "timestamp": 0,
    "last_image": "",
    "total_detections": 0,
    "detections": []  # List of current detections with bounding boxes
}
state_lock = Lock()

# ESP32-CAM configuration
ESP32_STREAM_URL = "http://10.43.145.165:81/stream"

@app.route('/stream')
def stream():
    """Stream with detection overlays"""
    def generate():
        """Generate annotated video stream using requests"""
        print(f"[STREAM] Client connected! Fetching ESP32 stream: {ESP32_STREAM_URL}")
        
        try:
            # Use requests to get MJPEG stream (more reliable than cv2.VideoCapture)
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=10)
            print("[STREAM] ESP32 stream connected successfully!")
            
            frame_count = 0
            bytes_buffer = b''
            
            
            for chunk in response.iter_content(chunk_size=1024):
                bytes_buffer += chunk
                
                # Find JPEG boundaries
                a = bytes_buffer.find(b'\xff\xd8')  # JPEG start
                b = bytes_buffer.find(b'\xff\xd9')  # JPEG end
                
                if a != -1 and b != -1:
                    jpg = bytes_buffer[a:b+2]
                    bytes_buffer = bytes_buffer[b+2:]
                    
                    # Decode JPEG
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frame_count += 1
                        if frame_count % 30 == 0:
                            print(f"[STREAM] Streaming... frame {frame_count}")
                        
                        # Draw detection boxes on frame
                        with state_lock:
                            detections = detection_state.get("detections", [])
                            
                            for det in detections:
                                label = det.get("label", "unknown")
                                conf = det.get("conf", 0.0)
                                tid = det.get("tid", 0)
                                bbox = det.get("bbox", [])
                                
                                if len(bbox) == 4:
                                    x1, y1, x2, y2 = bbox
                                    
                                    # Choose color based on label
                                    if label == "person":
                                        color = (0, 0, 255)  # Red for person
                                    elif label == "boat":
                                        color = (255, 165, 0)  # Orange for boat
                                    else:
                                        color = (0, 255, 0)  # Green for others
                                    
                                    # Draw rectangle
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                                    
                                    # Draw label background
                                    label_text = f"{label}#{tid} {int(conf*100)}%"
                                    (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                                    cv2.rectangle(frame, (x1, y1-25), (x1+w+10, y1), color, -1)
                                    
                                    # Draw label text
                                    cv2.putText(frame, label_text, (x1+5, y1-7),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            # Draw detection status banner
                            if detection_state.get("humanDetected", False):
                                cv2.rectangle(frame, (10, 10), (400, 60), (0, 0, 255), -1)
                                cv2.putText(frame, "HUMAN DETECTED!", (20, 45),
                                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                        
                        # Encode frame as JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        frame_bytes = buffer.tobytes()
                        
                        # Yield frame in MJPEG format
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        except Exception as e:
            print(f"[ERROR] Stream error: {e}")
            # Generate error frame
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Stream Error", (200, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame',
                   headers={
                       'Access-Control-Allow-Origin': '*',
                       'Cache-Control': 'no-cache, no-store, must-revalidate',
                       'Pragma': 'no-cache',
                       'Expires': '0'
                   })


@app.route('/status', methods=['GET'])
def status():
    """Return current detection state"""
    with state_lock:
        # Auto-clear detection after 3 seconds
        if detection_state["humanDetected"]:
            if time.time() - detection_state["timestamp"] > 3:
                detection_state["humanDetected"] = False
        
        return jsonify(detection_state)

@app.route('/update', methods=['POST'])
def update():
    """Receive detection updates from Python script"""
    global detection_state
    
    try:
        data = request.json
        with state_lock:
            # Update detection state
            detection_state["humanDetected"] = data.get("humanDetected", False)
            detection_state["label"] = data.get("label", "")
            detection_state["confidence"] = data.get("confidence", 0.0)
            detection_state["track_id"] = data.get("track_id", 0)
            detection_state["timestamp"] = data.get("timestamp", time.time())
            detection_state["last_image"] = data.get("last_image", "")
            detection_state["detections"] = data.get("detections", [])
            
            if data.get("humanDetected"):
                detection_state["total_detections"] += 1
        
        print(f"[UPDATE] Detection received: {data.get('label')} #{data.get('track_id')} ({data.get('confidence', 0)*100:.1f}%)")
        return jsonify({"status": "ok", "message": "Detection state updated"})
    
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "ESP32-CAM Detection API",
        "timestamp": time.time()
    })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset detection state"""
    global detection_state
    with state_lock:
        detection_state = {
            "humanDetected": False,
            "label": "",
            "confidence": 0.0,
            "track_id": 0,
            "timestamp": 0,
            "last_image": "",
            "total_detections": 0
        }
    return jsonify({"status": "ok", "message": "State reset"})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Flask Web API Server Starting...")
    print("=" * 60)
    print(f"📡 Stream proxy: http://0.0.0.0:5000/stream")
    print(f"📊 Status endpoint: http://0.0.0.0:5000/status")
    print(f"📥 Update endpoint: http://0.0.0.0:5000/update (POST)")
    print(f"💚 Health check: http://0.0.0.0:5000/health")
    print("=" * 60)
    print("\n✅ Server ready! Connect your React app to http://localhost:5000\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
