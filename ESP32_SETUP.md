# ESP32-CAM Quick Setup Guide

## Hardware Requirements
- ESP32-CAM module
- FTDI programmer or USB-to-Serial adapter
- 5V power supply (at least 2A)
- MicroSD card (optional, for saving images)

## Arduino IDE Setup

### 1. Install ESP32 Board Support
1. Open Arduino IDE
2. Go to **File > Preferences**
3. Add to **Additional Board Manager URLs**:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Go to **Tools > Board > Boards Manager**
5. Search for "ESP32" and install "esp32 by Espressif Systems"

### 2. Install Required Libraries
- Go to **Sketch > Include Library > Manage Libraries**
- Install these libraries:
  - `WiFi` (built-in)
  - `WebServer` (built-in)
  - `esp_camera` (built-in with ESP32)

## Basic Code for Stream with Human Detection

```cpp
#include <WiFi.h>
#include <WebServer.h>
#include "esp_camera.h"
#include "esp_http_server.h"

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Camera pins for AI-Thinker model
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

WebServer server(80);
httpd_handle_t stream_httpd = NULL;

bool humanDetected = false;

void setCrossOrigin() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}

void handleStatus() {
  setCrossOrigin();
  
  String json = "{";
  json += "\"humanDetected\":" + String(humanDetected ? "true" : "false") + ",";
  json += "\"timestamp\":" + String(millis());
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleOptions() {
  setCrossOrigin();
  server.send(204);
}

esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

 
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  
  res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
  if (res != ESP_OK) {
    return res;
  }

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      res = ESP_FAIL;
      break;
    }

    if (fb->format != PIXFORMAT_JPEG) {
      bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
      esp_camera_fb_return(fb);
      fb = NULL;
      if (!jpeg_converted) {
        Serial.println("JPEG compression failed");
        res = ESP_FAIL;
      }
    } else {
      _jpg_buf_len = fb->len;
      _jpg_buf = fb->buf;
    }

    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 64, 
        "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 13);
    }
    
    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    
    if (res != ESP_OK) {
      break;
    }
  }
  return res;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

void setup() {
  Serial.begin(115200);
  
  // Camera configuration
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size and quality
  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  // Start camera stream server
  startCameraServer();
  
  // Setup status endpoint
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/status", HTTP_OPTIONS, handleOptions);
  server.begin();
}

void loop() {
  server.handleClient();
  
  // YOUR HUMAN DETECTION LOGIC HERE
  // This is where you'd integrate your ML model
  // For example, if using TensorFlow Lite:
  /*
  camera_fb_t * fb = esp_camera_fb_get();
  if (fb) {
    // Run your detection model
    bool detected = runHumanDetection(fb);
    humanDetected = detected;
    esp_camera_fb_return(fb);
  }
  */
  
  // For testing, toggle detection every 10 seconds
  static unsigned long lastToggle = 0;
  if (millis() - lastToggle > 10000) {
    humanDetected = !humanDetected;
    lastToggle = millis();
    Serial.println(humanDetected ? "Human detected!" : "No human");
  }
}
```

## Uploading Code

1. **Board Settings**:
   - Board: "AI Thinker ESP32-CAM"
   - Upload Speed: 115200
   - Flash Frequency: 80MHz
   - Flash Mode: QIO
   - Partition Scheme: "Huge APP (3MB No OTA)"

2. **Wiring for Upload**:
   - Connect FTDI TX to ESP32 RX (GPIO3)
   - Connect FTDI RX to ESP32 TX (GPIO1)
   - Connect GND to GND
   - Connect 5V to 5V
   - Connect GPIO0 to GND (boot mode)

3. **Upload Process**:
   - Click Upload in Arduino IDE
   - Wait for "Connecting..."
   - Press RESET button on ESP32-CAM
   - After upload, disconnect GPIO0 from GND
   - Press RESET again

## Finding Your ESP32-CAM IP

After uploading, open Serial Monitor (115200 baud) and press RESET. You'll see:
```
Camera Ready! Use 'http://192.168.1.xxx' to connect
```

## Testing the Stream

1. Open browser to `http://<ESP32_IP>/stream`
2. You should see the camera feed
3. Test status: `http://<ESP32_IP>/status`

## Integrating ML Models

For actual human detection, you can use:

1. **Edge Impulse** - Train custom models
2. **TensorFlow Lite for Microcontrollers**
3. **ESP-WHO** (Espressif's face detection library)
4. **YOLO Tiny** models optimized for ESP32

## Troubleshooting

- **Camera init failed**: Check wiring, try different power supply
- **Brown out detector**: Power supply insufficient, use 2A adapter
- **Can't upload**: Make sure GPIO0 is connected to GND during upload
- **WiFi won't connect**: Check SSID/password, ensure 2.4GHz network

## Power Requirements

- Minimum: 5V 1A (may cause brownouts)
- Recommended: 5V 2A
- Use USB power bank or dedicated power supply
- Don't power from Arduino/FTDI during operation

## Next Steps

1. Upload the code to your ESP32-CAM
2. Note the IP address from Serial Monitor
3. Enter that IP in the React web app
4. Click "Connect" to start streaming!

---

Good luck with your InnoTech Rover project! 🚀
