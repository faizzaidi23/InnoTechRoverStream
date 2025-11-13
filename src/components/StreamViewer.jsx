import { useEffect, useRef } from 'react'
import './StreamViewer.css'

function StreamViewer({ espIp, isConnected, streamRef, onImageLoad }) {
  const imgRef = useRef(null)
  const reloadInterval = useRef(null)

  useEffect(() => {
    if (isConnected && imgRef.current) {
      // Show the stream image
      imgRef.current.classList.add('active')
      
      // Set up automatic reload for MJPEG stream
      // Most ESP32-CAM setups use MJPEG streams at /stream endpoint
      const streamUrl = `http://${espIp}/stream`
      imgRef.current.src = streamUrl
      
      // Alternatively, for periodic refresh (if not MJPEG):
      // reloadInterval.current = setInterval(() => {
      //   if (imgRef.current) {
      //     imgRef.current.src = `http://${espIp}/capture?t=${Date.now()}`
      //   }
      // }, 100) // 10 FPS
      
    } else if (imgRef.current) {
      imgRef.current.classList.remove('active')
      imgRef.current.src = ''
      
      if (reloadInterval.current) {
        clearInterval(reloadInterval.current)
      }
    }

    return () => {
      if (reloadInterval.current) {
        clearInterval(reloadInterval.current)
      }
    }
  }, [isConnected, espIp])

  return (
    <div className="video-container">
      <img
        ref={imgRef}
        id="stream"
        alt="ESP32-CAM Stream"
        onLoad={onImageLoad}
        onError={() => console.log('Stream error - check ESP32-CAM IP and connection')}
      />
      {!isConnected && (
        <div id="no-stream" className="no-stream-message">
          <p>📹 No Stream Connected</p>
          <p className="help-text">Enter your ESP32-CAM IP address and click Connect</p>
        </div>
      )}
    </div>
  )
}

export default StreamViewer
