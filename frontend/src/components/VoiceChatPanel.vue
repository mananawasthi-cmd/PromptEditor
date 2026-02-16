<template>
  <aside class="voice-panel">
    <header class="panel-header">
      <span class="panel-title">Voice Chat</span>
      <button class="icon-btn" title="Close" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </header>

    <div class="voice-body">
      <div v-if="!promptContent?.trim()" class="empty-state">
        <div class="empty-icon">🎤</div>
        <h3>Practice your pitch</h3>
        <p>Select a prompt (your pitch) from the sidebar to start a voice conversation.</p>
      </div>

      <template v-else>
        <div class="messages-wrap">
          <div
            v-for="(m, i) in messages"
            :key="i"
            class="msg-row"
            :class="m.role"
          >
            <div class="msg-avatar" :class="m.role">
              <svg v-if="m.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a3 3 0 0 1 3 3v1a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="22" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
              </svg>
            </div>
            <div class="msg-content">
              <div class="msg-text">{{ m.content }}</div>
            </div>
          </div>
          <div v-if="isStreaming" class="msg-row assistant">
            <div class="msg-avatar assistant">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
              </svg>
            </div>
            <div class="msg-content">
              <div class="msg-text">{{ streamingContent }}{{ streamingContent ? '▌' : '…' }}</div>
            </div>
          </div>
        </div>

        <div class="mic-area">
          <button
            class="mic-btn"
            :class="{ recording: isRecording, disabled: isStreaming || isPlaying }"
            :title="isRecording ? 'Stop' : 'Hold to speak'"
            @mousedown="startRecording"
            @mouseup="stopRecording"
            @mouseleave="stopRecording"
            @touchstart.prevent="startRecording"
            @touchend.prevent="stopRecording"
          >
            <svg v-if="!isRecording" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="22" />
            </svg>
            <span v-else class="mic-pulse" />
          </button>
          <p class="mic-hint">{{ isRecording ? 'Listening...' : 'Hold mic to speak' }}</p>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from 'vue'
import { streamVoiceChat } from '../api/chat'
import { textToSpeech } from '../api/tts'
import { useTtsSettings } from '../composables/useTtsSettings'

const props = defineProps({
  promptContent: { type: String, default: '' },
})

defineEmits(['close'])

const { voiceId, voiceSpeed } = useTtsSettings()
const messages = ref([])
const isRecording = ref(false)
const isStreaming = ref(false)
const isPlaying = ref(false)
const streamingContent = ref('')
let recognition = null
let currentAudio = null

function getRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) return null
  const r = new SpeechRecognition()
  r.continuous = false
  r.interimResults = false
  r.lang = 'en-US'
  return r
}

function startRecording() {
  if (isStreaming.value || isPlaying.value) return
  recognition = recognition || getRecognition()
  if (!recognition) {
    alert('Speech recognition not supported. Use Chrome.')
    return
  }
  recognition.onresult = (e) => {
    const text = e.results[0][0].transcript?.trim()
    if (text) processVoiceInput(text)
  }
  recognition.onerror = () => {}
  recognition.start()
  isRecording.value = true
}

function stopRecording() {
  if (recognition && isRecording.value) {
    try { recognition.stop() } catch (_) {}
  }
  isRecording.value = false
}

async function processVoiceInput(text) {
  messages.value.push({ role: 'user', content: text })
  isStreaming.value = true
  streamingContent.value = ''

  const history = messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

  try {
    let full = ''
    for await (const chunk of streamVoiceChat({
      promptContent: props.promptContent,
      message: text,
      messages: history,
    })) {
      if (chunk.content) {
        full += chunk.content
        streamingContent.value = full
      }
      if (chunk.error) {
        messages.value.push({ role: 'assistant', content: `Error: ${chunk.error}` })
        break
      }
    }
    if (full) {
      messages.value.push({ role: 'assistant', content: full })
      await playResponse(full)
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
  } finally {
    isStreaming.value = false
    streamingContent.value = ''
  }
}

async function playResponse(text) {
  const vid = voiceId.value.trim()
  if (!vid) return
  isPlaying.value = true
  try {
    const blob = await textToSpeech(text, vid, voiceSpeed.value)
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    currentAudio = audio
    await new Promise((resolve, reject) => {
      audio.onended = () => { URL.revokeObjectURL(url); resolve() }
      audio.onerror = reject
      audio.play()
    })
  } catch (_) {}
  finally {
    currentAudio = null
    isPlaying.value = false
  }
}
</script>

<style scoped>
.voice-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  border-left: 1px solid var(--border);
  min-width: 280px;
}

.panel-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-elevated);
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.icon-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.icon-btn svg {
  width: 16px;
  height: 16px;
}

.voice-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.msg-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.msg-avatar {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.msg-avatar.user {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.msg-avatar.assistant {
  background: var(--accent-muted);
  color: var(--accent);
}

.msg-avatar svg {
  width: 14px;
  height: 14px;
}

.msg-content {
  flex: 1;
  min-width: 0;
}

.msg-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.mic-area {
  flex-shrink: 0;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
}

.mic-btn {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: none;
  background: var(--accent);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.mic-btn:hover:not(.disabled) {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.mic-btn.recording {
  background: #ef4444;
  animation: pulse 1s ease-in-out infinite;
}

.mic-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mic-btn svg {
  width: 28px;
  height: 28px;
}

.mic-pulse {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
}

@keyframes pulse {
  50% { transform: scale(1.1); }
}

.mic-hint {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
