# 🎯 Updated Integration Instructions

## ✅ What's New:
The Flask backend now **draws bounding boxes directly on the video stream**! 

When you update your Python script, you'll see:
- ✅ **Red rectangles** around detected humans on the website stream
- ✅ **Orange rectangles** around boats
- ✅ **Green rectangles** around dogs
- ✅ **Labels with confidence %** on each detection
- ✅ **"🚨 HUMAN DETECTED!"** banner on the video when human is found
- ✅ **Detection alerts** in the sidebar panel

---

## 📝 Update Your Python Detection Script

### **Step 1: Add the Global Variable** (at the top with other globals)

```python
# Global variable to track all current detections for the web
current_web_detections = []
```

### **Step 2: Add the Updated Function** (replace the old update_web_status)

```python
def update_web_status(label, conf, tid, bbox):
    """
    Send detection event to Flask web API with bounding box
    
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
    except:
        pass  # Flask server might not be running
```

### **Step 3: Update Your Detection Loop**

Find this section (around line 120-140):

```python
if cid in wanted_ids:
    label = names[cid]
    x1, y1, x2, y2 = map(int, box.tolist())
    
    # ... your existing code ...
    
    # FIND THIS:
    send_telegram_async(img_path, conf, label, tid)
    
    # CHANGE TO THIS:
    send_telegram_async(img_path, conf, label, tid)
    update_web_status(label, conf, tid, [x1, y1, x2, y2])  # ← UPDATED WITH BBOX
    
    last_alert[tid] = now
```

---

## 🚀 How to Run:

### **Terminal 1: Flask Backend** ✅ (Already Running)
```powershell
cd backend
python web_api.py
```

### **Terminal 2: Your Python Detection Script** (Update it first!)
```powershell
python your_detection_script.py
```

### **Terminal 3: React Website** ✅ (Already Running)
```powershell
npm run dev
# Open http://localhost:3001
```

---

## 🎨 What You'll See:

### **On the Website Stream:**
- Red boxes around humans with labels like "person#1 95%"
- Orange boxes around boats
- Green boxes around dogs
- Red banner at top saying "🚨 HUMAN DETECTED!" when active

### **In the Sidebar:**
- Real-time detection alerts
- Detection history with timestamps
- Statistics and counts

### **Voice Alerts:**
- Browser speaks when detection occurs
- Customizable message and voice settings

---

## 📋 Quick Summary:

**Only 3 changes to your Python script:**
1. Add `current_web_detections = []` global variable
2. Replace `update_web_status()` function (now includes bbox parameter)
3. Change function call from:
   ```python
   update_web_status(label, conf, tid)
   ```
   to:
   ```python
   update_web_status(label, conf, tid, [x1, y1, x2, y2])
   ```

---

## ✅ Your Python Script Will Still:
- Show CV2 window with detections
- Play voice alerts (pyttsx3)
- Send Telegram notifications
- Save snapshots to disk
- **PLUS: Now updates the website with bounding boxes!**

---

## 🎉 Ready!

Refresh the website (`http://localhost:3001`) and you should see the bounding boxes drawn on the stream when you run your updated Python script!
