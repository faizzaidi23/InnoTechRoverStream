#!/usr/bin/env python3
"""
Milestone 5A++ (ESP32-CAM Version) - Web Integrated
----------------------------------
• Reads MJPEG stream from ESP32-CAM
• Speaks 3× per detected person (5-sec gaps)
• Sends Telegram alerts + saves snapshots
• Sends detection data to Flask backend for website display
"""

import os, csv, time, cv2, requests, threading, random
from datetime import datetime
from collections import deque

# Import YOLO with multiprocessing fix
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()

from ultralytics import YOLO
import pyttsx3

# ---------- CONFIG ----------
ESP32_STREAM_URL = "http://10.43.145.165:81/stream"   # 🔁 change this!
MODEL_NAME = "yolov8n.pt"
CONF_THRESHOLD = 0.4
COOLDOWN_SEC = 2.0

DETECT_CLASSES = ["person", "boat", "dog"]
VOICE_LINES = {
    "person": "Hello boss, human detected in flood.",
    "boat":   "Rescue boat detected on water.",
    "dog":    "Animal detected, possible survivor nearby."
}

FRAME_WIDTH, FRAME_HEIGHT = 1200, 900
OUTPUT_DIR = "detections"
LOG_FILE = os.path.join(OUTPUT_DIR, "detections_log.csv")

BOT_TOKEN = "8532473590:AAHlzSJKUXNiQpDctAaurM-0YjkgVD7pcN8"
CHAT_ID   = "1231762023"

# WEB INTEGRATION
FLASK_BACKEND_URL = "http://localhost:5000/update"
# --------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp","label","confidence","track_id","image_path"])

# Global variable to track current detections for web
current_web_detections = []

# ----- Voice Setup -----
def speak_three_times(label, tid):
    for i in range(3):
        try:
            eng = pyttsx3.init()
            eng.setProperty("rate", 165)
            eng.setProperty("volume", 1.0)
            eng.say(VOICE_LINES.get(label, f"{label} detected"))
            eng.runAndWait()
            eng.stop()
        except Exception as e:
            print("[VOICE ERROR]", e)
        time.sleep(5)
    print(f"[VOICE] Finished 3× speech for {label}#{tid}")

def speak_threaded(label, tid):
    threading.Thread(target=speak_three_times, args=(label, tid), daemon=True).start()

# ----- Telegram -----
def send_telegram_async(img_path, conf, label, track_id):
    def worker():
        try:
            msg = (f"🚨 {label.capitalize()} detected!\n"
                   f"Confidence: {conf:.2f}\nID: {track_id}\n"
                   f"Time: {datetime.now().strftime('%H:%M:%S')}")
            with open(img_path, "rb") as photo:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": CHAT_ID, "caption": msg},
                    files={"photo": photo},
                    timeout=10,
                )
            print(f"[TG] Alert sent for {label} #{track_id}")
        except Exception as e:
            print("[TG] Error:", e)
    threading.Thread(target=worker, daemon=True).start()

# ----- WEB INTEGRATION -----
def update_web_status(label, conf, tid, bbox):
    """Send detection data to Flask backend for website display"""
    global current_web_detections
    
    # Add to current detections list
    detection_data = {
        "bbox": bbox,  # [x1, y1, x2, y2]
        "label": label,
        "conf": conf,
        "tid": tid
    }
    
    # Keep only recent detections (last 10)
    current_web_detections.append(detection_data)
    if len(current_web_detections) > 10:
        current_web_detections.pop(0)
    
    # Prepare payload for Flask
    payload = {
        "humanDetected": (label == "person"),
        "label": label,
        "confidence": conf,
        "track_id": tid,
        "timestamp": datetime.now().isoformat(),
        "detections": current_web_detections
    }
    
    # Send to Flask backend (non-blocking)
    def send_to_flask():
        try:
            requests.post(FLASK_BACKEND_URL, json=payload, timeout=1)
            print(f"[WEB] Sent {label}#{tid} to backend")
        except Exception as e:
            print(f"[WEB] Failed to update backend: {e}")
    
    threading.Thread(target=send_to_flask, daemon=True).start()

# ----- YOLO + Tracker -----
print("🔄 Loading YOLOv8n model...")
model = YOLO(MODEL_NAME)
names = model.names
wanted_ids = {cid for cid, name in names.items() if name in DETECT_CLASSES}
print("✅ Model loaded. Tracking:", [names[i] for i in wanted_ids])

cap = cv2.VideoCapture(ESP32_STREAM_URL)
if not cap.isOpened():
    raise SystemExit(f"❌ Cannot open ESP32-CAM stream: {ESP32_STREAM_URL}")
print("✅ Connected to ESP32-CAM stream.")

# Tracking memory
last_alert = {}
track_colors = {}
trail_memory = {}
speech_memory = {}   # {tid: {"spoken": bool}}

fps_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠  Stream read error — reconnecting...")
            time.sleep(0.5)
            cap.release()
            cap = cv2.VideoCapture(ESP32_STREAM_URL)
            continue

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        results = model.track(frame, persist=True, conf=CONF_THRESHOLD, verbose=False)
        annotated = results[0].plot()

        # Clear current detections at start of each frame
        current_web_detections = []

        if hasattr(results[0], "boxes") and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            for i, box in enumerate(boxes.xyxy):
                cid = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                tid = int(boxes.id[i].item()) if boxes.id is not None else i

                if cid in wanted_ids:
                    label = names[cid]
                    x1, y1, x2, y2 = map(int, box.tolist())

                    # unique color
                    if tid not in track_colors:
                        track_colors[tid] = (random.randint(0,255),
                                             random.randint(0,255),
                                             random.randint(0,255))
                    color = track_colors[tid]
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(annotated, f"{label}#{tid}", (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                    # motion trail
                    cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                    if tid not in trail_memory:
                        trail_memory[tid] = deque(maxlen=20)
                    trail_memory[tid].append((cx, cy))
                    for j in range(1, len(trail_memory[tid])):
                        cv2.line(annotated, trail_memory[tid][j-1],
                                 trail_memory[tid][j], color, 2)

                    # --- Smart Voice Logic ---
                    if tid not in speech_memory:
                        speech_memory[tid] = {"spoken": False}
                        print(f"[VOICE] New {label}#{tid} detected → starting 3× speech")
                        speak_threaded(label, tid)
                        speech_memory[tid]["spoken"] = True

                    # --- Telegram + Snapshot ---
                    now = time.time()
                    if tid not in last_alert or now - last_alert[tid] > COOLDOWN_SEC:
                        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                        img_name = f"{label}{tid}{ts}_{int(conf*100)}.jpg"
                        img_path = os.path.join(OUTPUT_DIR, img_name)
                        cv2.imwrite(img_path, frame)
                        with open(LOG_FILE, "a", newline="") as f:
                            csv.writer(f).writerow([ts, label, f"{conf:.3f}", tid, img_path])
                        print(f"[SNAP] {label}#{tid} ({conf:.2f}) saved")
                        send_telegram_async(img_path, conf, label, tid)
                        last_alert[tid] = now
                        
                        # Send to web backend
                        update_web_status(label, conf, tid, [x1, y1, x2, y2])

        # Show FPS
        fps = 1.0 / max(1e-6, time.time() - fps_time)
        fps_time = time.time()
        cv2.putText(annotated, f"FPS:{int(fps)}", (10,25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),2)
        cv2.imshow("ESP32-CAM Smart Detection", annotated)
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("🔚 Exiting gracefully.")
