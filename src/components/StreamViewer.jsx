import { useEffect, useRef } from 'react'
import './StreamViewer.css'

function StreamViewer({ espIp, isConnected, streamRef, onImageLoad }) {
  const imgRef = useRef(null)
  const reloadInterval = useRef(null)

  useEffect(() => {
    if (isConnected && imgRef.current) {
      // Show the stream image
      imgRef.current.classList.add('active')
      
      // Connect to Flask backend stream endpoint
      const streamUrl = `${espIp}/stream`
      imgRef.current.src = streamUrl
      
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
          <p className="help-text">Enter Flask backend URL and click Connect</p>
        </div>
      )}
    </div>
  )
}

export default StreamViewer
