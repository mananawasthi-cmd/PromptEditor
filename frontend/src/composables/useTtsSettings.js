import { ref, watch } from 'vue'

const STORAGE_KEY = 'prompt-editor-tts-voice-id'
const SPEED_KEY = 'prompt-editor-tts-speed'

let voiceIdRef = null
let voiceSpeedRef = null
const openSettingsRef = ref(false)

export function useTtsSettings() {
  if (!voiceIdRef) {
    voiceIdRef = ref(localStorage.getItem(STORAGE_KEY) || '')
    watch(voiceIdRef, (v) => {
      if (v?.trim()) {
        localStorage.setItem(STORAGE_KEY, v.trim())
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    }, { immediate: true })
  }
  if (!voiceSpeedRef) {
    const saved = parseFloat(localStorage.getItem(SPEED_KEY) || '1')
    voiceSpeedRef = ref(isNaN(saved) || saved < 0.5 || saved > 2 ? 1 : saved)
    watch(voiceSpeedRef, (v) => {
      localStorage.setItem(SPEED_KEY, String(v))
    }, { immediate: true })
  }
  return { voiceId: voiceIdRef, voiceSpeed: voiceSpeedRef, openSettings: openSettingsRef }
}
