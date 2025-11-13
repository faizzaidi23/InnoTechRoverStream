import { useState, useCallback, useRef } from 'react'

function useVoiceAlert() {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true)
  const [alertMessage, setAlertMessage] = useState('Human detected!')
  const [voiceRate, setVoiceRate] = useState(1.0)
  const [voicePitch, setVoicePitch] = useState(1.0)
  const [lastAlertTime, setLastAlertTime] = useState(null)
  
  const isSpeaking = useRef(false)
  const lastSpeakTime = useRef(0)

  const speak = useCallback((message) => {
    // Prevent speaking if already speaking or if less than 3 seconds since last alert
    const now = Date.now()
    if (isSpeaking.current || (now - lastSpeakTime.current < 3000)) {
      return
    }

    // Check if browser supports speech synthesis
    if (!window.speechSynthesis) {
      console.warn('Speech synthesis not supported in this browser')
      return
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    // Create utterance
    const utterance = new SpeechSynthesisUtterance(message)
    utterance.rate = voiceRate
    utterance.pitch = voicePitch
    utterance.volume = 1.0
    utterance.lang = 'en-US'

    // Set speaking state
    isSpeaking.current = true
    lastSpeakTime.current = now
    setLastAlertTime(new Date().toLocaleTimeString())

    utterance.onend = () => {
      isSpeaking.current = false
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event)
      isSpeaking.current = false
    }

    // Speak the message
    window.speechSynthesis.speak(utterance)
  }, [voiceRate, voicePitch])

  const testVoice = useCallback(() => {
    speak(alertMessage)
  }, [speak, alertMessage])

  return {
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
  }
}

export default useVoiceAlert
