import './DetectionPanel.css'

function DetectionPanel({
  detectionStatus,
  isVoiceEnabled,
  setIsVoiceEnabled,
  alertMessage,
  setAlertMessage,
  voiceRate,
  setVoiceRate,
  voicePitch,
  setVoicePitch,
  testVoice,
  lastAlertTime,
  streamFps
}) {
  return (
    <div className="detection-panel">
      <h2>Detection Status</h2>
      <div className={`detection-box ${detectionStatus.detected ? 'active' : ''}`}>
        <div className="detection-icon">
          {detectionStatus.detected ? '🚨' : '👤'}
        </div>
        <p className="detection-text">
          {detectionStatus.detected ? 'HUMAN DETECTED!' : 'No Detection'}
        </p>
        <p className="detection-time">{detectionStatus.lastDetection}</p>
      </div>

      <div className="settings-box">
        <h3>Voice Alert Settings</h3>
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={isVoiceEnabled}
              onChange={(e) => setIsVoiceEnabled(e.target.checked)}
            />
            Enable Voice Alerts
          </label>
        </div>
        <div className="setting-item">
          <label htmlFor="alert-message">Alert Message:</label>
          <input
            type="text"
            id="alert-message"
            value={alertMessage}
            onChange={(e) => setAlertMessage(e.target.value)}
            placeholder="Custom alert message"
          />
        </div>
        <div className="setting-item">
          <label htmlFor="voice-rate">Speech Rate:</label>
          <input
            type="range"
            id="voice-rate"
            min="0.5"
            max="2"
            step="0.1"
            value={voiceRate}
            onChange={(e) => setVoiceRate(parseFloat(e.target.value))}
          />
          <span>{voiceRate.toFixed(1)}x</span>
        </div>
        <div className="setting-item">
          <label htmlFor="voice-pitch">Speech Pitch:</label>
          <input
            type="range"
            id="voice-pitch"
            min="0"
            max="2"
            step="0.1"
            value={voicePitch}
            onChange={(e) => setVoicePitch(parseFloat(e.target.value))}
          />
          <span>{voicePitch.toFixed(1)}</span>
        </div>
        <button id="test-voice" onClick={testVoice}>
          Test Voice Alert
        </button>
      </div>

      <div className="stats-box">
        <h3>Statistics</h3>
        <div className="stat-item">
          <span className="stat-label">Total Detections:</span>
          <span className="stat-value">{detectionStatus.totalDetections}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Last Alert:</span>
          <span className="stat-value">{lastAlertTime || 'Never'}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Stream FPS:</span>
          <span className="stat-value">{streamFps}</span>
        </div>
      </div>
    </div>
  )
}

export default DetectionPanel
