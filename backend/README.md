# Flask Backend for ESP32-CAM Detection

This backend serves as a bridge between your Python ML detection script and the React frontend.

## Installation

```powershell
pip install -r requirements.txt
```

## Running the Server

```powershell
python web_api.py
```

The server will start on `http://localhost:5000`

## Endpoints

- `GET /stream` - Proxied ESP32-CAM video stream
- `GET /status` - Current detection status (JSON)
- `POST /update` - Receive detection updates from ML script
- `GET /health` - Health check

## Integration with Your Detection Script

Add these lines to your existing Python detection script:

```python
import requests

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
        pass

# In your detection loop, after sending Telegram alert:
send_telegram_async(img_path, conf, label, tid)
update_web_status(label, conf, tid)  # Add this line
last_alert[tid] = now
```
