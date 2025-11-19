import { useEffect, useState } from 'react'
import './DetectionAlert.css'

function DetectionAlert({ backendUrl, isVoiceEnabled, alertMessage, voiceRate, voicePitch }) {
  const [detection, setDetection] = useState(null)
  const [history, setHistory] = useState([])
  const [lastAlertTime, setLastAlertTime] = useState(null)

  useEffect(() => {
    if (!backendUrl) return

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${backendUrl}/status`)
        const data = await res.json()
        
        if (data.humanDetected) {
          // Check if this is a new detection
          const isNewDetection = !detection || 
            detection.track_id !== data.track_id || 
            detection.timestamp !== data.timestamp

          setDetection(data)

          // Add to history if new
          if (isNewDetection) {
            setHistory(prev => {
              // Avoid duplicates
              const exists = prev.find(h => 
                h.track_id === data.track_id && 
                h.timestamp === data.timestamp
              )
              if (!exists) {
                return [data, ...prev].slice(0, 10) // Keep last 10
              }
              return prev
            })

            // Trigger voice alert
            if (isVoiceEnabled) {
              const message = alertMessage || 
                `${data.label} detected with ${Math.round(data.confidence * 100)} percent confidence`
              
              const utterance = new SpeechSynthesisUtterance(message)
              utterance.rate = voiceRate || 1.0
              utterance.pitch = voicePitch || 1.0
              utterance.volume = 1.0
              window.speechSynthesis.speak(utterance)
              
              setLastAlertTime(new Date().toLocaleTimeString())
            }
          }
        } else {
          setDetection(null)
        }
      } catch (err) {
        console.error('Status check failed:', err)
      }
    }, 1000) // Poll every second

    return () => clearInterval(interval)
  }, [backendUrl, detection, isVoiceEnabled, alertMessage, voiceRate, voicePitch])

  return (
    <div className="detection-alert-container">
      {/* Active Detection Alert */}
      {detection && (
        <div className="detection-alert-banner pulse">
          <div className="alert-icon">🚨</div>
          <div className="alert-content">
            <h2>{detection.label.toUpperCase()} DETECTED!</h2>
            <div className="alert-details">
              <span className="detail-badge">
                Confidence: {(detection.confidence * 100).toFixed(1)}%
              </span>
              <span className="detail-badge">
                ID: #{detection.track_id}
              </span>
              <span className="detail-badge">
                {new Date(detection.timestamp * 1000).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Detection History */}
      <div className="detection-history-panel">
        <h3>📋 Recent Detections</h3>
        {history.length === 0 ? (
          <p className="no-detections">No detections yet. Monitoring stream...</p>
        ) : (
          <div className="history-list">
            {history.map((det, i) => (
              <div key={`${det.track_id}-${det.timestamp}-${i}`} className="history-item">
                <div className="history-icon">
                  {det.label === 'person' ? '👤' : det.label === 'boat' ? '🚤' : '🐕'}
                </div>
                <div className="history-details">
                  <div className="history-label">{det.label}</div>
                  <div className="history-meta">
                    <span className="history-confidence">
                      {(det.confidence * 100).toFixed(0)}%
                    </span>
                    <span className="history-id">ID: {det.track_id}</span>
                    <span className="history-time">
                      {new Date(det.timestamp * 1000).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Last Voice Alert Time */}
      {lastAlertTime && (
        <div className="last-alert-info">
          <span>🔊 Last voice alert: {lastAlertTime}</span>
        </div>
      )}
    </div>
  )
}

export default DetectionAlert
