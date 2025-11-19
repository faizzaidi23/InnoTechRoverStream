# 🚀 Complete Setup Guide - ESP32-CAM ML Detection Website

## What You Have Now

✅ **Flask Backend** - Bridges your Python ML script and React website  
✅ **React Frontend** - Beautiful web interface with real-time detection alerts  
✅ **Detection Alerts** - Shows "HUMAN DETECTED!" banner when ML model detects  
✅ **Voice Alerts** - Browser announces detections  
✅ **Detection History** - Last 10 detections with timestamps  

---

## 📋 Step-by-Step Setup

### **Step 1: Install Flask Backend Dependencies**

```powershell
cd backend
pip install -r requirements.txt
```

### **Step 2: Start Flask Backend Server**

```powershell
python web_api.py
```

You should see:
```
🚀 Flask Web API Server Starting...
📡 Stream proxy: http://0.0.0.0:5000/stream
📊 Status endpoint: http://0.0.0.0:5000/status
✅ Server ready!
```

**Keep this terminal running!**

---

### **Step 3: Update Your Python Detection Script**

Add these lines to your existing detection script:

```python
import requests  # Add at top

# Add this function after send_telegram_async
def update_web_status(label, conf, tid):
    """Send detection to web API"""
    try:
        requests.post('http://localhost:5000/update', json={
            "humanDetected": True,
            "label": label,
            "confidence": float(conf),
            "track_id": int(tid),
            "timestamp": time.time()
        }, timeout=1)
    except:
        pass  # Flask might not be running

# In your detection loop, find this line:
#     send_telegram_async(img_path, conf, label, tid)
#     last_alert[tid] = now
#
# Change it to:
#     send_telegram_async(img_path, conf, label, tid)
#     update_web_status(label, conf, tid)  # ← ADD THIS
#     last_alert[tid] = now
```

**That's it! Only 2 lines added to your Python script.**

---

### **Step 4: Start Your Python Detection Script**

```powershell
# In a NEW terminal
python your_detection_script.py
```

Your Python script will continue working exactly as before:
- ✅ CV2 window shows detections
- ✅ Voice alerts (pyttsx3) still work
- ✅ Telegram notifications still work
- ✅ Snapshots still saved
- **➕ Now also sends detection events to the website!**

---

### **Step 5: Start React Website**

```powershell
# In a NEW terminal
cd ..
npm run dev
```

The website will open at `http://localhost:3000`

---

### **Step 6: Connect to the Stream**

1. Open `http://localhost:3000` in your browser
2. In the "Flask Backend URL" field, enter: `http://localhost:5000`
3. Click **"Connect"**
4. You should see:
   - ✅ Live ESP32-CAM stream
   - ✅ "Connected" status in green

---

### **Step 7: Test Detection**

When your Python script detects a human:

**On Python side:**
- CV2 window shows bounding box
- Voice alert speaks 3 times
- Telegram message sent
- Snapshot saved

**On Website:**
- 🚨 **Red "HUMAN DETECTED!" banner appears**
- 🔊 **Browser speaks the detection**
- 📋 **Detection added to history panel**
- ✅ **Shows: label, confidence, track ID, timestamp**

---

## 🖥️ Running Everything

You need **3 terminals** running simultaneously:

```powershell
# Terminal 1: Flask Backend
cd backend
python web_api.py

# Terminal 2: Your Python ML Detection Script  
python your_detection_script.py

# Terminal 3: React Frontend
npm run dev
```

---

## 🌐 Deploy to the Web (Optional)

### **Deploy Flask Backend to Render**

1. Go to [render.com](https://render.com) and sign up
2. Click "New Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_api.py`
   - **Instance Type**: Free
5. Add environment variable:
   - Key: `ESP32_STREAM_URL`
   - Value: Your ESP32 stream URL (use ngrok if needed)
6. Click "Create Web Service"
7. You'll get a URL like: `https://your-app.onrender.com`

### **Deploy React to Vercel**

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

Follow prompts, and you'll get a URL like: `https://your-site.vercel.app`

### **Update React to Use Deployed Backend**

In the deployed React app, change the backend URL from `http://localhost:5000` to your Render URL `https://your-app.onrender.com`

---

## 🔧 Troubleshooting

### Stream Not Showing
- Check Flask server is running (`python web_api.py`)
- Verify ESP32-CAM is on and streaming
- Check backend URL in React app is correct

### No Detection Alerts
- Make sure you added `update_web_status()` to your Python script
- Check Python script is running
- Verify Flask server received update (check terminal logs)

### CORS Errors
- Flask-CORS should handle this automatically
- If issues persist, restart Flask server

### Voice Alerts Not Working
- Use Chrome or Edge browser (best Web Speech API support)
- Check "Enable Voice Alerts" is toggled ON in settings
- Test with "Test Voice Alert" button

---

## 📊 What Happens When Detection Occurs

```
┌─────────────────────────────┐
│  ESP32-CAM                  │
│  Streams video continuously │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Your Python Script         │
│  • Runs YOLO detection      │
│  • Shows CV2 window         │ ──→ Voice Alert (pyttsx3)
│  • Calls update_web_status()│ ──→ Telegram Alert
└──────────┬──────────────────┘ ──→ Saves Snapshot
           │
           ▼
┌─────────────────────────────┐
│  Flask Backend              │
│  • Receives detection event │
│  • Updates global state     │
│  • Proxies ESP32 stream     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  React Website              │
│  • Polls /status every 1sec │
│  • Shows detection banner   │ ──→ Voice Alert (browser)
│  • Updates history          │ ──→ Visual Animation
└─────────────────────────────┘
```

---

## ✅ Checklist

- [ ] Flask backend running (`python web_api.py`)
- [ ] Python detection script updated with `update_web_status()`
- [ ] Python detection script running
- [ ] React dev server running (`npm run dev`)
- [ ] Connected to backend in React app
- [ ] Stream visible on website
- [ ] Test detection appears on website

---

## 🎉 You're All Set!

Your website now shows:
- 📹 Live ESP32-CAM stream
- 🚨 Real-time detection alerts
- 🔊 Voice announcements
- 📊 Detection history
- 📈 Statistics and FPS

**And your Python script continues working exactly as before!**

---

## 📞 Need Help?

Check the logs:
- Flask backend terminal (shows API requests)
- Python script terminal (shows detections)
- Browser console (F12 → Console tab)

---

## 🚀 Next Steps

Want to make it better?
- Add authentication to Flask API
- Deploy both to cloud services
- Add video recording feature
- Show detection bounding boxes on stream
- Add email alerts
- Create mobile app version

Enjoy your ML detection website! 🎊
