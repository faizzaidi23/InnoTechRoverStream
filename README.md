# InnoTech Rover - ESP32-CAM Stream Viewer

A modern React-based web application for viewing ESP32-CAM live streams with real-time human detection and voice alerts.

## Features

- 📹 **Live Video Streaming** - View real-time video feed from ESP32-CAM
- 👤 **Human Detection** - Visual indicator when humans are detected
- 🔊 **Voice Alerts** - Customizable voice notifications when detection occurs
- 📊 **Statistics** - Track total detections, FPS, and alert history
- 🎨 **Modern UI** - Beautiful, responsive design that works on all devices
- ⚙️ **Customizable** - Adjust voice pitch, rate, and alert messages

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- ESP32-CAM module with human detection capability

## Installation

1. Clone the repository:
```bash
git clone https://github.com/faizzaidi23/InnoTechRoverStream.git
cd InnoTechRoverStream
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:3000`

## Usage

1. **Enter ESP32-CAM IP Address**: Input your ESP32-CAM's IP address (e.g., `192.168.1.100`)
2. **Connect**: Click the "Connect" button to start streaming
3. **Configure Alerts**: Customize voice alert settings in the Detection Panel
4. **Monitor**: Watch the stream and receive alerts when humans are detected

## ESP32-CAM Configuration

### Stream Endpoints

Your ESP32-CAM should provide the following endpoints:

- **Stream Endpoint**: `http://<ESP32_IP>/stream` - MJPEG video stream
- **Status Endpoint** (Optional): `http://<ESP32_IP>/status` - JSON with detection status

### Status Endpoint Response Format

```json
{
  "humanDetected": true,
  "confidence": 0.95,
  "timestamp": 1234567890
}
```

### Example ESP32-CAM Arduino Code Setup

```cpp
#include <WiFi.h>
#include <WebServer.h>
#include "esp_camera.h"

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

WebServer server(80);
bool humanDetected = false;

void setup() {
  // Initialize camera
  camera_config_t config;
  // ... camera configuration ...
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  
  // Setup endpoints
  server.on("/stream", handleStream);
  server.on("/status", handleStatus);
  
  server.begin();
}

void handleStream() {
  // Stream MJPEG
}

void handleStatus() {
  String json = "{\"humanDetected\":" + String(humanDetected ? "true" : "false") + "}";
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void loop() {
  server.handleClient();
  // Your human detection logic here
  // Set humanDetected = true when human is detected
}
```

### CORS Configuration

Make sure your ESP32-CAM allows CORS by adding these headers:

```cpp
server.sendHeader("Access-Control-Allow-Origin", "*");
server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
```

## Voice Alert Settings

- **Enable/Disable**: Toggle voice alerts on/off
- **Custom Message**: Change the alert message text
- **Speech Rate**: Adjust how fast the voice speaks (0.5x - 2.0x)
- **Speech Pitch**: Modify the voice pitch (0.0 - 2.0)
- **Test Button**: Test your alert settings before detection

## Building for Production

```bash
npm run build
```

The optimized production files will be in the `dist` folder.

## Deployment

### Deploy to GitHub Pages

1. Install gh-pages:
```bash
npm install --save-dev gh-pages
```

2. Add to package.json:
```json
{
  "scripts": {
    "deploy": "vite build && gh-pages -d dist"
  },
  "homepage": "https://yourusername.github.io/InnoTechRoverStream"
}
```

3. Deploy:
```bash
npm run deploy
```

### Deploy to Netlify/Vercel

Simply connect your GitHub repository and these platforms will auto-deploy.

## Troubleshooting

### Stream Not Showing

- Verify ESP32-CAM IP address is correct
- Ensure ESP32-CAM and computer are on same network
- Check if ESP32-CAM is powered on and connected to WiFi
- Try accessing `http://<ESP32_IP>/stream` directly in browser

### CORS Errors

- Add CORS headers to ESP32-CAM responses (see configuration above)
- Use the same network for both devices
- Check browser console for specific error messages

### No Voice Alerts

- Ensure browser supports Web Speech API (Chrome, Edge recommended)
- Check if "Enable Voice Alerts" is toggled on
- Test voice with the "Test Voice Alert" button
- Check browser permissions for audio

### Detection Not Working

- Verify `/status` endpoint is implemented on ESP32-CAM
- Check that detection logic is running on ESP32-CAM
- Confirm JSON response format matches expected structure
- Monitor browser console for API errors

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Voice alerts work best in Chrome/Edge

## Technologies Used

- **React** - UI framework
- **Vite** - Build tool and dev server
- **Web Speech API** - Voice alerts
- **CSS3** - Styling and animations

## License

MIT License - feel free to use this project for your own purposes!

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review ESP32-CAM documentation

## Acknowledgments

- ESP32-CAM community for camera module support
- React team for the awesome framework
- Web Speech API for voice synthesis capabilities

---

Made with ❤️ by InnoTech Rover Team
