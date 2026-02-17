<template>
  <div class="editor">
    <template v-if="loading">
      <div class="editor-loading">
        <div class="spinner"></div>
        <p>Loading...</p>
      </div>
    </template>
    <template v-else-if="!prompt">
      <div class="editor-empty">
        <h3>No prompt selected</h3>
        <p>Choose a prompt from the sidebar or create a new one to get started.</p>
        <button class="btn-primary" @click="$emit('create')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New Prompt
        </button>
      </div>
    </template>
    <template v-else>
      <header class="editor-header">
        <input
          v-model="title"
          class="editor-title"
          placeholder="Untitled prompt"
          @blur="emitSave"
        />
      </header>
      <div class="editor-write-area" ref="writeAreaRef" @scroll="onWriteAreaScroll">
        <div class="write-area-inner" ref="writeInnerRef">
          <div ref="lineNumbersRef" class="line-numbers">
            <div class="line-numbers-inner" :style="{ minHeight: lineNumbersHeight }">
              <span v-for="n in lineCount" :key="n" class="line-num">{{ n }}</span>
            </div>
          </div>
          <div class="editor-content-wrap">
          <textarea
            ref="textareaRef"
            v-model="content"
            class="editor-content"
            placeholder="Start writing your prompt here...

• Be specific about what you want
• Include examples if helpful
• Add context or constraints
• Select text → ⌘K edit with AI, ⌘L listen"
            spellcheck="false"
            @blur="emitSave"
            @mouseup="onSelectionChange"
            @keyup="onSelectionChange"
            @select="onSelectionChange"
            @scroll="onTextareaScroll"
          />
          </div>
          <Transition name="tts-fade">
            <div v-if="selectedText && !quickEditOpen" class="tts-floating" :style="ttsPosition" role="toolbar">
            <button
              class="tts-btn tts-edit-btn"
              title="Edit with AI (⌘K)"
              @click="openQuickEdit"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
              Edit
            </button>
            <template v-if="ttsError">
              <span class="tts-error-text">{{ ttsError }}</span>
              <button class="tts-btn tts-retry-btn" @click="retryTts">Retry</button>
            </template>
            <template v-else-if="!voiceId.trim()">
              <button class="tts-btn tts-set-voice-btn" @click="openSettings = true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                </svg>
                Set Voice to Listen
              </button>
            </template>
            <template v-else>
              <button
                v-if="isPlaying"
                class="tts-btn tts-stop-btn"
                title="Stop playback"
                @click="stopTts"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
                Stop
              </button>
              <button
                v-else
                class="tts-btn tts-play-btn"
                title="Listen to selection (⌘L)"
                @click="playTts"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
                Listen
              </button>
            </template>
            </div>
          </Transition>
          <Transition name="tts-fade">
            <div v-if="quickEditOpen" class="quick-edit-panel" :style="quickEditPosition">
              <div class="quick-edit-header">
                <span class="quick-edit-label">Edit with AI</span>
                <button class="quick-edit-close" @click="closeQuickEdit" title="Cancel">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
              <div class="quick-edit-preview">Editing: {{ selectedText.slice(0, 60) }}{{ selectedText.length > 60 ? '…' : '' }}</div>
              <div class="quick-edit-messages">
                <div
                  v-for="(m, i) in quickEditMessages"
                  :key="i"
                  class="qe-msg"
                  :class="m.role"
                >
                  <span class="qe-msg-role">{{ m.role === 'user' ? 'You' : 'AI' }}</span>
                  <div class="qe-msg-content">{{ m.content }}</div>
                </div>
                <div v-if="quickEditLoading" class="qe-msg assistant">
                  <span class="qe-msg-role">AI</span>
                  <div class="qe-msg-content">{{ quickEditStreaming }}{{ quickEditStreaming ? '▌' : '…' }}</div>
                </div>
              </div>
              <div class="quick-edit-input-wrap">
                <input
                  ref="quickEditInputRef"
                  v-model="quickEditInstruction"
                  class="quick-edit-input"
                  :placeholder="quickEditMessages.length ? 'Refine the edit...' : 'e.g. make it concise, fix grammar...'"
                  @keydown.enter.exact.prevent="runQuickEdit"
                  @keydown.escape="closeQuickEdit"
                />
                <button
                  class="quick-edit-send"
                  :disabled="!quickEditInstruction.trim() || quickEditLoading"
                  @click="runQuickEdit"
                >
                  <span v-if="quickEditLoading" class="spinner-small" />
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </button>
              </div>
              <div v-if="latestAiResponse" class="quick-edit-actions">
                <button class="btn-apply-inline" @click="applyQuickEdit">Approve & Replace</button>
                <button class="btn-cancel-inline" @click="closeQuickEdit">Cancel</button>
              </div>
              <div v-else-if="quickEditError" class="quick-edit-error">{{ quickEditError }}</div>
            </div>
          </Transition>
        </div>
        <div class="editor-stats">
          <span>{{ wordCount }} words</span>
          <span>{{ content.length }} characters</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { textToSpeech } from '../api/tts'
import { streamChat } from '../api/chat'
import { useTtsSettings } from '../composables/useTtsSettings'
import { useChatContext } from '../composables/useChatContext'

const props = defineProps({
  prompt: { type: Object, default: null },
  loading: Boolean,
})

const emit = defineEmits(['save', 'create', 'add-to-chat'])

defineExpose({
  applyEdit(payload) {
    if (payload.replaceAll) {
      content.value = payload.replacement
    } else {
      const start = payload.selectionStart ?? 0
      const end = payload.selectionEnd ?? content.value.length
      content.value = content.value.slice(0, start) + payload.replacement + content.value.slice(end)
    }
    emitSave()
  },
})
const { voiceId, voiceSpeed, openSettings } = useTtsSettings()
const { setChatContext } = useChatContext()

const title = ref('')
const content = ref('')
const textareaRef = ref(null)
const lineNumbersRef = ref(null)
const writeAreaRef = ref(null)
const writeInnerRef = ref(null)
const selectedText = ref('')
const isPlaying = ref(false)
const ttsError = ref('')
const ttsPosition = ref({ top: '0px', left: '0px' })
let currentAudio = null

const quickEditOpen = ref(false)
const quickEditInstruction = ref('')
const quickEditMessages = ref([])
const quickEditStreaming = ref('')
const quickEditError = ref('')
const quickEditLoading = ref(false)
const quickEditInputRef = ref(null)
const quickEditPosition = ref({ top: '0px', left: '0px' })


const latestAiResponse = computed(() => {
  if (quickEditStreaming.value) return quickEditStreaming.value
  const assistants = quickEditMessages.value.filter(m => m.role === 'assistant')
  return assistants.length ? assistants[assistants.length - 1].content : ''
})

const wordCount = computed(() => {
  const text = content.value.trim()
  if (!text) return 0
  return text.split(/\s+/).filter(Boolean).length
})

const lineCount = computed(() => {
  const lines = content.value.split('\n')
  return Math.max(1, lines.length)
})

const lineNumbersHeight = computed(() => {
  const lineHeight = 1.7
  const lineHeightPx = 14 * lineHeight
  return `${lineCount.value * lineHeightPx}px`
})

function onSelectionChange() {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = content.value.slice(start, end).trim()
  selectedText.value = text || ''
  ttsError.value = ''
  if (text) {
    nextTick(() => updateTtsPosition())
  }
}

function onWriteAreaScroll() {
  if (selectedText.value) nextTick(updateTtsPosition)
}

function onTextareaScroll() {
  if (selectedText.value) nextTick(updateTtsPosition)
  const ta = textareaRef.value
  const ln = lineNumbersRef.value
  if (ta && ln) ln.scrollTop = ta.scrollTop
}

function updateTtsPosition() {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = content.value
  const before = text.substring(0, start)
  const sel = text.substring(start, end)
  if (!sel.trim()) return

  const textareaRect = textarea.getBoundingClientRect()
  const mirror = document.createElement('div')
  const cs = getComputedStyle(textarea)
  mirror.style.cssText = `
    position: fixed;
    top: ${textareaRect.top}px;
    left: ${textareaRect.left}px;
    visibility: hidden;
    white-space: pre-wrap;
    word-wrap: break-word;
    font: ${cs.font};
    padding: ${cs.padding};
    width: ${textarea.offsetWidth}px;
    line-height: ${cs.lineHeight};
    letter-spacing: ${cs.letterSpacing};
    box-sizing: border-box;
    transform: translateY(-${textarea.scrollTop}px);
    pointer-events: none;
  `
  mirror.textContent = before
  const span = document.createElement('span')
  span.textContent = sel
  mirror.appendChild(span)
  document.body.appendChild(mirror)
  const rect = span.getBoundingClientRect()
  document.body.removeChild(mirror)

  const toolbarHeight = 44
  const gap = 8
  const spaceAbove = rect.top
  const spaceBelow = window.innerHeight - rect.bottom
  const showAbove = spaceAbove >= spaceBelow || spaceBelow < toolbarHeight + gap
  const top = showAbove
    ? Math.max(8, rect.top - toolbarHeight - gap)
    : Math.min(window.innerHeight - toolbarHeight - 8, rect.bottom + gap)
  const left = Math.max(8, Math.min(rect.left, window.innerWidth - 160))
  ttsPosition.value = {
    top: `${top}px`,
    left: `${left}px`,
  }
}

function openQuickEdit() {
  if (!selectedText.value) return
  quickEditOpen.value = true
  quickEditInstruction.value = ''
  quickEditMessages.value = []
  quickEditStreaming.value = ''
  quickEditError.value = ''
  nextTick(() => {
    const topNum = parseInt(ttsPosition.value.top, 10) || 0
    quickEditPosition.value = { ...ttsPosition.value, top: `${topNum + 48}px` }
    quickEditInputRef.value?.focus()
  })
}

function closeQuickEdit() {
  quickEditOpen.value = false
  quickEditInstruction.value = ''
  quickEditMessages.value = []
  quickEditStreaming.value = ''
  quickEditError.value = ''
}

async function runQuickEdit() {
  const instruction = quickEditInstruction.value.trim()
  if (!instruction || quickEditLoading.value) return

  const el = textareaRef.value
  if (!el) return

  quickEditMessages.value.push({ role: 'user', content: instruction })
  quickEditInstruction.value = ''
  quickEditLoading.value = true
  quickEditStreaming.value = ''
  quickEditError.value = ''

  const history = quickEditMessages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

  try {
    let streamed = ''
    for await (const chunk of streamChat({
      promptContent: content.value,
      selectedText: selectedText.value,
      message: instruction,
      messages: history,
    })) {
      if (chunk.content) {
        streamed += chunk.content
        quickEditStreaming.value = streamed
      }
      if (chunk.error) quickEditError.value = chunk.error
    }
    if (streamed) {
      quickEditMessages.value.push({ role: 'assistant', content: streamed })
    }
  } catch (e) {
    quickEditError.value = e.message || 'Failed'
  } finally {
    quickEditLoading.value = false
    quickEditStreaming.value = ''
  }
}

function applyQuickEdit() {
  const replacement = latestAiResponse.value
  if (!replacement) return
  const el = textareaRef.value
  if (!el) return
  content.value = content.value.slice(0, el.selectionStart) + replacement + content.value.slice(el.selectionEnd)
  emitSave()
  closeQuickEdit()
  selectedText.value = ''
}

function onAddToChat() {
  const el = textareaRef.value
  if (!el) return
  setChatContext({
    promptContent: content.value,
    selectedText: selectedText.value,
    selectionStart: el.selectionStart,
    selectionEnd: el.selectionEnd,
  })
  emit('add-to-chat')
}

function retryTts() {
  ttsError.value = ''
  playTts()
}

function stopTts() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
  isPlaying.value = false
}

function onKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'l') {
    if (selectedText.value && voiceId.value.trim()) {
      e.preventDefault()
      playTts()
    }
  }
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    const el = textareaRef.value
    if (el) {
      e.preventDefault()
      if (!selectedText.value && content.value) {
        el.setSelectionRange(0, content.value.length)
        selectedText.value = content.value
        nextTick(() => { updateTtsPosition(); openQuickEdit() })
      } else if (selectedText.value) {
        openQuickEdit()
      }
    }
  }
  if ((e.metaKey || e.ctrlKey) && e.key === 'l') {
    if (selectedText.value) {
      e.preventDefault()
      if (voiceId.value.trim()) playTts()
      else onAddToChat()
    }
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

watch(
  () => props.prompt,
  (p) => {
    if (p) {
      title.value = p.title ?? ''
      content.value = p.content ?? ''
    }
    selectedText.value = ''
    ttsError.value = ''
    closeQuickEdit()
  },
  { immediate: true }
)

async function playTts() {
  const text = selectedText.value
  const vid = voiceId.value.trim()
  if (!text || !vid) return
  ttsError.value = ''
  isPlaying.value = true
  try {
    const blob = await textToSpeech(text, vid, voiceSpeed.value)
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    currentAudio = audio
    const done = () => {
      URL.revokeObjectURL(url)
      currentAudio = null
      isPlaying.value = false
    }
    audio.onended = done
    audio.onerror = done
    await audio.play()
  } catch (err) {
    isPlaying.value = false
    currentAudio = null
    ttsError.value = err.message || 'TTS failed. Check Voice ID in settings.'
  }
}

function emitSave() {
  if (!props.prompt) return
  const t = title.value.trim() || 'Untitled'
  const c = content.value
  if (t !== props.prompt.title || c !== props.prompt.content) {
    emit('save', { id: props.prompt.id, title: t, content: c })
  }
}
</script>

<style scoped>
.editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--bg-base);
}

.editor-loading,
.editor-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.editor-loading {
  gap: 16px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.editor-loading p {
  font-size: 13px;
  color: var(--text-muted);
}

.editor-empty h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.editor-empty p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  max-width: 280px;
  line-height: 1.5;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background var(--transition);
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-primary svg {
  width: 16px;
  height: 16px;
}

.editor-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-elevated);
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.editor-title {
  flex: 1;
  min-width: 120px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  font-family: inherit;
  outline: none;
}

.editor-title::placeholder {
  color: var(--text-muted);
}

.editor-write-area {
  flex: 1;
  padding: 24px;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.write-area-inner {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: row;
  min-height: 200px;
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: visible;
  transition: border-color var(--transition);
}

.line-numbers {
  flex-shrink: 0;
  width: 40px;
  padding: 20px 8px 20px 24px;
  overflow-y: auto;
  overflow-x: hidden;
  user-select: none;
  color: var(--text-muted);
  font-size: 14px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  line-height: 1.7;
}

.line-numbers-inner {
  display: flex;
  flex-direction: column;
  text-align: right;
}

.line-num {
  display: block;
  min-height: 1.7em;
  padding-right: 4px;
}

.editor-content-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.write-area-inner:focus-within {
  border-color: var(--accent);
}

.editor-content {
  flex: 1;
  width: 100%;
  min-height: 260px;
  padding: 20px 24px 20px 16px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  line-height: 1.7;
  resize: none;
  outline: none;
}

.editor-content::placeholder {
  color: var(--text-muted);
}

.editor-content::selection {
  background: var(--accent-muted);
}

.tts-fade-enter-active,
.tts-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.tts-fade-enter-from,
.tts-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.tts-floating {
  position: fixed;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.tts-error-text {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 0 8px;
  max-width: 180px;
}

.tts-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-hover);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.tts-btn:hover {
  background: var(--accent-muted);
  color: var(--accent);
}

.tts-set-voice-btn:hover {
  color: var(--accent);
}

.tts-retry-btn {
  flex-shrink: 0;
}

.tts-play-btn svg,
.tts-stop-btn svg,
.tts-set-voice-btn svg,
.tts-edit-btn svg {
  width: 14px;
  height: 14px;
}

.quick-edit-panel {
  position: fixed;
  z-index: 1001;
  min-width: 320px;
  max-width: 480px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.quick-edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}

.quick-edit-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.quick-edit-close {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.quick-edit-close:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.quick-edit-close svg {
  width: 14px;
  height: 14px;
}

.quick-edit-preview {
  padding: 8px 12px;
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-base);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-edit-input-wrap {
  display: flex;
  gap: 8px;
  padding: 12px;
  align-items: center;
}

.quick-edit-input {
  flex: 1;
  padding: 8px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: border-color var(--transition);
}

.quick-edit-input:focus {
  border-color: var(--accent);
}

.quick-edit-input::placeholder {
  color: var(--text-muted);
}

.quick-edit-send {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  flex-shrink: 0;
}

.quick-edit-send:hover:not(:disabled) {
  background: var(--accent-hover);
}

.quick-edit-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-edit-send svg {
  width: 16px;
  height: 16px;
}

.quick-edit-messages {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
}

.qe-msg {
  margin-bottom: 10px;
}

.qe-msg:last-child {
  margin-bottom: 0;
}

.qe-msg-role {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  display: block;
  margin-bottom: 4px;
}

.qe-msg-content {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.quick-edit-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border);
}

.btn-apply-inline {
  padding: 6px 14px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

.btn-apply-inline:hover {
  background: var(--accent-hover);
}

.btn-cancel-inline {
  padding: 6px 14px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
}

.btn-cancel-inline:hover {
  background: var(--border);
  color: var(--text-primary);
}

.quick-edit-error {
  padding: 12px;
  font-size: 12px;
  color: #f87171;
  border-top: 1px solid var(--border);
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.tts-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.editor-stats {
  display: flex;
  gap: 16px;
  padding: 10px 24px;
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-elevated);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
</style>
