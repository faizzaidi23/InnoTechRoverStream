import { useState, useEffect, useRef } from 'react'
import Header from './components/Header'
import ConnectionPanel from './components/ConnectionPanel'
import StreamViewer from './components/StreamViewer'
import DetectionPanel from './components/DetectionPanel'
import Footer from './components/Footer'
import useVoiceAlert from './hooks/useVoiceAlert'
import './App.css'

function App() {
  const [espIp, setEspIp] = useState('192.168.1.100')
  const [isConnected, setIsConnected] = useState(false)
  const [detectionStatus, setDetectionStatus] = useState({
    detected: false,
    lastDetection: 'Waiting for stream...',
    totalDetections: 0
  })
  const [streamFps, setStreamFps] = useState(0)
  
  const { 
    speak, 
    isVoiceEnabled, 
    setIsVoiceEnabled, 
    alertMessage, 
    setAlertMessage,
    voiceRate,
    setVoiceRate,
    voicePitch,
    setVoicePitch,
    lastAlertTime,
    testVoice
  } = useVoiceAlert()

  const streamRef = useRef(null)
  const detectionCheckInterval = useRef(null)
  const fpsInterval = useRef(null)
  const frameCount = useRef(0)

  const connectToStream = () => {
    if (!espIp.trim()) {
      alert('Please enter a valid ESP32-CAM IP address')
      return
    }

    setIsConnected(true)
    
    // Start checking for detection messages from ESP32-CAM
    // The ESP32-CAM should send detection status via a separate endpoint or embed it in the stream
    detectionCheckInterval.current = setInterval(() => {
      checkForDetection()
    }, 1000) // Check every second

    // Start FPS counter
    startFpsCounter()
  }

  const disconnectStream = () => {
    setIsConnected(false)
    setStreamFps(0)
    
    if (detectionCheckInterval.current) {
      clearInterval(detectionCheckInterval.current)
    }
    
    if (fpsInterval.current) {
      clearInterval(fpsInterval.current)
    }

    setDetectionStatus({
      detected: false,
      lastDetection: 'Disconnected',
      totalDetections: detectionStatus.totalDetections
    })
  }

  const checkForDetection = async () => {
    try {
      // Try to fetch detection status from ESP32-CAM
      // This endpoint should be implemented on your ESP32-CAM
      const response = await fetch(`http://${espIp}/status`, {
        method: 'GET',
        mode: 'cors'
      })
      
      if (response.ok) {
        const data = await response.json()
        
        if (data.humanDetected && !detectionStatus.detected) {
          // New detection!
          const now = new Date().toLocaleTimeString()
          setDetectionStatus(prev => ({
            detected: true,
            lastDetection: now,
            totalDetections: prev.totalDetections + 1
          }))
          
          // Trigger voice alert
          if (isVoiceEnabled) {
            speak(alertMessage)
          }
          
          // Reset detection status after 3 seconds
          setTimeout(() => {
            setDetectionStatus(prev => ({
              ...prev,
              detected: false
            }))
          }, 3000)
        } else if (!data.humanDetected && detectionStatus.detected) {
          setDetectionStatus(prev => ({
            ...prev,
            detected: false
          }))
        }
      }
    } catch (error) {
      // If status endpoint doesn't exist, we'll rely on visual detection
      // or you can parse the stream URL for detection info
      console.log('Status check failed (this is normal if ESP32 doesn\'t have /status endpoint)')
    }
  }

  const startFpsCounter = () => {
    frameCount.current = 0
    
    fpsInterval.current = setInterval(() => {
      setStreamFps(frameCount.current)
      frameCount.current = 0
    }, 1000)
  }

  const handleImageLoad = () => {
    frameCount.current++
  }

  useEffect(() => {
    return () => {
      if (detectionCheckInterval.current) {
        clearInterval(detectionCheckInterval.current)
      }
      if (fpsInterval.current) {
        clearInterval(fpsInterval.current)
      }
    }
  }, [])

  return (
    <div className="container">
      <Header />
      
      <ConnectionPanel
        espIp={espIp}
        setEspIp={setEspIp}
        isConnected={isConnected}
        connectToStream={connectToStream}
        disconnectStream={disconnectStream}
      />

      <div className="main-content">
        <StreamViewer
          espIp={espIp}
          isConnected={isConnected}
          streamRef={streamRef}
          onImageLoad={handleImageLoad}
        />

        <DetectionPanel
          detectionStatus={detectionStatus}
          isVoiceEnabled={isVoiceEnabled}
          setIsVoiceEnabled={setIsVoiceEnabled}
          alertMessage={alertMessage}
          setAlertMessage={setAlertMessage}
          voiceRate={voiceRate}
          setVoiceRate={setVoiceRate}
          voicePitch={voicePitch}
          setVoicePitch={setVoicePitch}
          testVoice={testVoice}
          lastAlertTime={lastAlertTime}
          streamFps={streamFps}
        />
      </div>

      <Footer />
    </div>
  )
}

export default App
