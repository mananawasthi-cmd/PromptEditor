<template>
  <aside class="chat-panel">
    <header class="panel-header">
      <span class="panel-title">Chat</span>
      <button class="icon-btn" title="Close" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </header>

    <div class="chat-body">
      <div v-if="!messages.length && !isStreaming" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <h3>Edit prompts with AI</h3>
        <p>Select text in the editor and click <strong>Edit</strong> (⌘K) to edit with AI, or use the button below to add the full prompt.</p>
        <button class="btn-add-full" @click="addFullPromptToContext">
          Add full prompt to chat
        </button>
      </div>

      <div v-else class="messages-wrap">
        <div
          v-for="(m, i) in messages"
          :key="i"
          class="msg-row"
          :class="m.role"
        >
          <div class="msg-avatar" :class="m.role">
            <svg v-if="m.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
            </svg>
          </div>
          <div class="msg-content">
            <div class="msg-text">{{ m.content }}</div>
            <div v-if="m.role === 'assistant' && m.content" class="msg-actions">
              <button class="btn-apply" @click="applyEdit(m.content)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14" />
                  <path d="M12 5l7 7-7 7" />
                </svg>
                Apply to editor
              </button>
            </div>
          </div>
        </div>

        <div v-if="isStreaming" class="msg-row assistant">
          <div class="msg-avatar assistant">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
            </svg>
          </div>
          <div class="msg-content">
            <div class="msg-text">
              {{ streamingContent }}
              <span class="caret">▌</span>
            </div>
            <div v-if="streamingContent" class="msg-actions">
              <button class="btn-apply" @click="applyStreaming">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14" />
                  <path d="M12 5l7 7-7 7" />
                </svg>
                Apply to editor
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="input-wrap">
        <textarea
          ref="inputRef"
          v-model="inputText"
          class="chat-input"
          placeholder="Ask AI to edit... (e.g. make it concise, fix grammar)"
          rows="1"
          @keydown.enter.exact.prevent="send"
          @input="autoResize"
        />
        <button
          class="btn-send"
          :disabled="!canSend"
          :class="{ loading: isStreaming }"
          title="Send (Enter)"
          @click="send"
        >
          <svg v-if="!isStreaming" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
          <span v-else class="spinner-small" />
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { streamChat } from '../api/chat'
import { useChatContext } from '../composables/useChatContext'

const props = defineProps({
  promptContent: { type: String, default: '' },
})

const emit = defineEmits(['close', 'apply-edit'])

const { chatContext, setChatContext } = useChatContext()
const inputRef = ref(null)
const inputText = ref('')
const messages = ref([])
const isStreaming = ref(false)
const streamingContent = ref('')

const canSend = computed(() => inputText.value.trim().length > 0 && !isStreaming.value)

function addFullPromptToContext() {
  if (!props.promptContent?.trim()) {
    messages.value.push({
      role: 'assistant',
      content: 'No prompt open. Select a prompt from the sidebar first, or select text and click Edit (⌘K).',
    })
    return
  }
  setChatContext({
    promptContent: props.promptContent,
    selectedText: '',
    selectionStart: 0,
    selectionEnd: 0,
  })
  inputRef.value?.focus()
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

async function send() {
  const msg = inputText.value.trim()
  if (!msg || isStreaming.value) return

  const ctx = chatContext.value
  if (!ctx.promptContent && !ctx.selectedText) {
    setChatContext({
      promptContent: props.promptContent,
      selectedText: '',
      selectionStart: 0,
      selectionEnd: 0,
    })
  }

  const finalCtx = chatContext.value
  if (!finalCtx.promptContent && !finalCtx.selectedText) {
    messages.value.push({
      role: 'assistant',
      content: 'Add your prompt first: select text and click Edit (⌘K), or click "Add full prompt to chat".',
    })
    return
  }

  messages.value.push({ role: 'user', content: msg })
  inputText.value = ''
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  isStreaming.value = true
  streamingContent.value = ''

  try {
    for await (const chunk of streamChat({
      promptContent: finalCtx.promptContent,
      selectedText: finalCtx.selectedText,
      message: msg,
    })) {
      if (chunk.content) streamingContent.value += chunk.content
      if (chunk.error) {
        messages.value.push({ role: 'assistant', content: `Error: ${chunk.error}` })
        break
      }
    }
    if (streamingContent.value && !messages.value.some(m => m.role === 'assistant' && m.content?.includes('Error:'))) {
      messages.value.push({ role: 'assistant', content: streamingContent.value })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
  } finally {
    isStreaming.value = false
    streamingContent.value = ''
  }
}

function applyEdit(text) {
  const ctx = chatContext.value
  if (ctx.selectedText) {
    emit('apply-edit', {
      replacement: text,
      selectionStart: ctx.selectionStart,
      selectionEnd: ctx.selectionEnd,
    })
  } else {
    emit('apply-edit', { replacement: text, replaceAll: true })
  }
}

function applyStreaming() {
  applyEdit(streamingContent.value)
}
</script>

<style scoped>
.chat-panel {
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
  transition: all var(--transition);
}

.icon-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.icon-btn svg {
  width: 16px;
  height: 16px;
}

.chat-body {
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
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 24px;
  height: 24px;
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
  margin-bottom: 20px;
  max-width: 260px;
}

.btn-add-full {
  padding: 10px 18px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition);
}

.btn-add-full:hover {
  background: var(--accent-hover);
}

.messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.msg-row {
  display: flex;
  gap: 12px;
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
  word-break: break-word;
}

.msg-actions {
  margin-top: 10px;
}

.btn-apply {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--accent-muted);
  color: var(--accent);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.btn-apply:hover {
  background: var(--accent);
  color: white;
}

.btn-apply svg {
  width: 12px;
  height: 12px;
}

.caret {
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.input-wrap {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
}

.chat-input {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color var(--transition);
}

.chat-input:focus {
  border-color: var(--accent);
}

.chat-input::placeholder {
  color: var(--text-muted);
}

.btn-send {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition);
}

.btn-send:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-send.loading {
  cursor: wait;
}

.btn-send svg {
  width: 18px;
  height: 18px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
