import './ConnectionPanel.css'

function ConnectionPanel({ espIp, setEspIp, isConnected, connectToStream, disconnectStream }) {
  return (
    <div className="connection-panel">
      <div className="input-group">
        <label htmlFor="esp-ip">Flask Backend URL:</label>
        <input
          type="text"
          id="esp-ip"
          placeholder="e.g., http://localhost:5000"
          value={espIp}
          onChange={(e) => setEspIp(e.target.value)}
          disabled={isConnected}
        />
        <button
          id="connect-btn"
          onClick={connectToStream}
          disabled={isConnected}
        >
          Connect
        </button>
        <button
          id="disconnect-btn"
          onClick={disconnectStream}
          disabled={!isConnected}
        >
          Disconnect
        </button>
      </div>

      <div className="status-bar">
        <span className="status-label">Status:</span>
        <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
    </div>
  )
}

export default ConnectionPanel
