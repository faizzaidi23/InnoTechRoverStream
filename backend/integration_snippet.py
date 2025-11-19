"""
Integration snippet for your existing Python detection script
Add these functions and call update_web_status() when detection occurs
"""

import requests
import time

# Global variable to track all current detections for the web
current_web_detections = []

def update_web_status(label, conf, tid, bbox):
    """
    Send detection event to Flask web API with bounding box
    Call this function whenever you detect a person/boat/dog
    
    Args:
        label: Detection label (person, boat, dog)
        conf: Confidence score (0.0 - 1.0)
        tid: Track ID
        bbox: Bounding box as [x1, y1, x2, y2]
    """
    global current_web_detections
    
    # Add or update this detection in the list
    detection_info = {
        "label": label,
        "confidence": float(conf),
        "track_id": int(tid),
        "bbox": [int(x) for x in bbox]
    }
    
    # Update or add detection
    found = False
    for i, det in enumerate(current_web_detections):
        if det["track_id"] == tid:
            current_web_detections[i] = detection_info
            found = True
            break
    
    if not found:
        current_web_detections.append(detection_info)
    
    try:
        requests.post('http://localhost:5000/update', json={
            "humanDetected": True,
            "label": label,
            "confidence": float(conf),
            "track_id": int(tid),
            "timestamp": time.time(),
            "detections": current_web_detections  # Send all current detections
        }, timeout=1)
        print(f"[WEB] Sent detection update: {label}#{tid} with bbox")
    except Exception as e:
        # Flask server might not be running - that's okay
        pass


def clear_old_web_detections():
    """
    Call this periodically to remove stale detections
    Add this in your main loop
    """
    global current_web_detections
    current_time = time.time()
    
    # Remove detections older than 3 seconds
    # (Implement your own tracking logic based on your needs)
    pass


# ============================================
# MODIFY YOUR EXISTING DETECTION LOOP
# ============================================
# 
# Find this section in your code (around line 100-140):
#
# if hasattr(results[0], "boxes") and len(results[0].boxes) > 0:
#     boxes = results[0].boxes
#     for i, box in enumerate(boxes.xyxy):
#         cid = int(boxes.cls[i].item())
#         conf = float(boxes.conf[i].item())
#         tid = int(boxes.id[i].item()) if boxes.id is not None else i
#
#         if cid in wanted_ids:
#             label = names[cid]
#             x1, y1, x2, y2 = map(int, box.tolist())
#
#             # ... existing code ...
#
#             # FIND THIS LINE (around line 130):
#             send_telegram_async(img_path, conf, label, tid)
#             
#             # ADD THIS LINE RIGHT AFTER:
#             update_web_status(label, conf, tid, [x1, y1, x2, y2])  # ← ADD THIS
#             
#             last_alert[tid] = now
#
# ============================================

# That's it! Your detection will now appear on the website with bounding boxes!
