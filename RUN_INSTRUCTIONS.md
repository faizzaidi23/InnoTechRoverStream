# 🚀 Running Your Complete Detection System

## System Overview
Your system has **3 components** that work together:
1. **Flask Backend** (port 5000) - Receives detection data and serves video stream
2. **React Frontend** (port 3001) - Displays the website
3. **Python Detection Script** - Runs YOLOv8 detection on ESP32-CAM stream

## ✅ Current Status

### Already Running:
- ✅ Flask Backend: `http://localhost:5000` (running)
- ✅ React Frontend: `http://localhost:3001` (running)

### Ready to Start:
- ⏳ Detection Script: `detection_script.py` (ready to run)

## 🎯 How to Start Everything

### Step 1: Verify Backend & Frontend (Already Running)
Your Flask backend and React frontend are already running! You can verify:
- Open browser: `http://localhost:3001`
- You should see the InnoTech Rover website

### Step 2: Run the Detection Script
Open a **new terminal** and run:

```powershell
python detection_script.py
```

This will:
- ✅ Connect to ESP32-CAM stream at `http://10.43.145.165:81/stream`
- ✅ Run YOLOv8 object detection (person, boat, dog)
- ✅ Show detection window with bounding boxes and trails
- ✅ Speak 3× voice alerts for each new detection
- ✅ Send Telegram alerts with snapshots
- ✅ **Send detection data to Flask backend for website display**

### Step 3: Use the Website
1. Open browser: `http://localhost:3001`
2. The backend URL should already be set to `http://localhost:5000`
3. Click **Connect**
4. You'll see:
   - 📹 Live stream with bounding boxes drawn by Flask
   - 🚨 Detection alerts when humans/boats/dogs are detected
   - 🔊 Voice announcements in the browser
   - 📊 Detection history panel

## 🔧 What Was Added to Your Script

### Three Key Integrations:

1. **Global Detection Tracking** (line 39):
   ```python
   current_web_detections = []
   ```

2. **Web Update Function** (lines 80-113):
   ```python
   def update_web_status(label, conf, tid, bbox):
       # Sends detection data to Flask backend
       # Including bounding box coordinates [x1, y1, x2, y2]
   ```

3. **Auto-Send After Each Detection** (line 213):
   ```python
   update_web_status(label, conf, tid, [x1, y1, x2, y2])
   ```

### What Happens Now:
- When your script detects a person/boat/dog, it:
  1. ✅ Shows in CV2 window (as before)
  2. ✅ Speaks 3× alert (as before)
  3. ✅ Sends Telegram message (as before)
  4. ✅ Saves snapshot (as before)
  5. ✅ **NEW: Sends to Flask backend for website display**

## 📊 Data Flow

```
ESP32-CAM Stream
      ↓
Python Script (YOLOv8)
      ↓
[Detections with bounding boxes]
      ↓
Flask Backend ← Receives detection data via POST
      ↓
[Draws boxes on stream]
      ↓
React Frontend ← Displays annotated stream + alerts
```

## 🎨 Visual Features on Website

When a detection occurs, you'll see:
- **Red rectangles** around humans
- **Orange rectangles** around boats
- **Green rectangles** around dogs
- **Labels with confidence** (e.g., "person#1 92%")
- **Red banner** at top: "🚨 HUMAN DETECTED!"
- **Detection alerts** in right sidebar
- **Voice announcements** from browser

## 🛠️ Troubleshooting

### If Detection Script Fails to Start:
```powershell
# Install required packages
pip install ultralytics opencv-python pyttsx3 requests
```

### If ESP32-CAM IP Changed:
Edit line 18 in `detection_script.py`:
```python
ESP32_STREAM_URL = "http://YOUR_NEW_IP:81/stream"
```

### If Flask Backend Stopped:
```powershell
cd backend
python web_api.py
```

### If React Frontend Stopped:
```powershell
npm run dev
```

## 🎯 Testing Checklist

1. [ ] Flask backend running (check terminal output)
2. [ ] React frontend running (check terminal output)
3. [ ] Website loads at `http://localhost:3001`
4. [ ] Click "Connect" on website
5. [ ] Run `python detection_script.py`
6. [ ] CV2 window appears with ESP32 stream
7. [ ] Detections appear in CV2 window
8. [ ] Bounding boxes appear on website stream
9. [ ] Detection alerts appear in sidebar
10. [ ] Voice announcements play in browser

## 📝 Notes

- **All original features preserved**: Your script still does everything it did before (CV2 window, voice, Telegram, snapshots)
- **Web integration is non-blocking**: If Flask backend is down, script continues working normally
- **Bounding boxes**: Flask backend draws the boxes on the stream, so you see them on the website
- **Real-time updates**: Website polls every 1 second for new detections

## 🎉 Ready to Go!

Your complete system is ready. Just run:

```powershell
python detection_script.py
```

Then open `http://localhost:3001` in your browser and click Connect!
