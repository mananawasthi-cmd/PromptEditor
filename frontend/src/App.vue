<template>
  <div class="app">
    <header class="app-header">
      <div class="app-brand">
        <span class="app-logo">Prompt</span>
        <span class="app-suffix">Editor</span>
      </div>
      <div class="app-header-right">
        <SettingsDropdown />
        <footer class="app-footer">
          <span class="copyright">© 2026</span>
          <span class="built-by">Built by Manan</span>
        </footer>
      </div>
    </header>
    <div class="app-body">
      <ActivityBar
        :active-view="activeView"
        :chat-panel-open="chatPanelOpen"
        :voice-panel-open="voicePanelOpen"
        @view-change="activeView = $event"
        @chat-panel-toggle="toggleChatPanel"
        @voice-panel-toggle="toggleVoicePanel"
      />

      <template v-if="sidebarOpen">
        <Sidebar
          :prompts="prompts"
          :selected-id="selectedPromptId"
          :style="{ width: sidebarWidth + 'px' }"
          @close="sidebarOpen = false"
          @select="selectPrompt"
          @create="createPrompt"
        />
        <div
          class="resize-handle resize-handle-left"
          title="Drag to resize"
          @mousedown="startResizeSidebar"
        >
          <div class="resize-line" />
        </div>
      </template>

      <main class="main-area">
        <Editor
          ref="editorRef"
          :prompt="currentPrompt"
          :loading="loading"
          @save="savePrompt"
          @create="createPrompt"
          @add-to-chat="chatPanelOpen = true"
        />
      </main>

      <template v-if="chatPanelOpen">
        <div
          class="resize-handle resize-handle-right"
          title="Drag to resize"
          @mousedown="startResizeChat"
        >
          <div class="resize-line" />
        </div>
        <ChatPanel
          :style="{ width: chatPanelWidth + 'px' }"
          :prompt-content="currentPrompt?.content ?? ''"
          @close="chatPanelOpen = false"
          @apply-edit="onApplyEdit"
        />
      </template>
      <template v-if="voicePanelOpen">
        <div
          class="resize-handle resize-handle-right"
          title="Drag to resize"
          @mousedown="startResizeChat"
        >
          <div class="resize-line" />
        </div>
        <VoiceChatPanel
          :style="{ width: chatPanelWidth + 'px' }"
          :prompt-content="currentPrompt?.content ?? ''"
          @close="voicePanelOpen = false"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ActivityBar from './components/ActivityBar.vue'
import SettingsDropdown from './components/SettingsDropdown.vue'
import Sidebar from './components/Sidebar.vue'
import Editor from './components/Editor.vue'
import ChatPanel from './components/ChatPanel.vue'
import VoiceChatPanel from './components/VoiceChatPanel.vue'
import { fetchPrompts, createPrompt as apiCreate, updatePrompt } from './api/prompts'

const STORAGE_KEY = 'prompt-editor-panel-sizes'

const sidebarOpen = ref(true)
const chatPanelOpen = ref(true)
const voicePanelOpen = ref(false)
const activeView = ref('prompts')
const prompts = ref([])
const selectedPromptId = ref(null)
const loading = ref(false)

const sidebarWidth = ref(260)
const chatPanelWidth = ref(340)
const editorRef = ref(null)

const currentPrompt = computed(() => {
  if (!selectedPromptId.value) return null
  return prompts.value.find(p => p.id === selectedPromptId.value) ?? null
})

function loadSizes() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const { sidebar, chat } = JSON.parse(saved)
      if (sidebar >= 180 && sidebar <= 500) sidebarWidth.value = sidebar
      if (chat >= 200 && chat <= 600) chatPanelWidth.value = chat
    }
  } catch {}
}

function saveSizes() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    sidebar: sidebarWidth.value,
    chat: chatPanelWidth.value,
  }))
}

function startResizeSidebar(e) {
  e.preventDefault()
  const startX = e.clientX
  const startW = sidebarWidth.value
  function move(e) {
    const dx = e.clientX - startX
    sidebarWidth.value = Math.max(180, Math.min(500, startW + dx))
  }
  function up() {
    document.removeEventListener('mousemove', move)
    document.removeEventListener('mouseup', up)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    saveSizes()
  }
  document.addEventListener('mousemove', move)
  document.addEventListener('mouseup', up)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function startResizeChat(e) {
  e.preventDefault()
  const startX = e.clientX
  const startW = chatPanelWidth.value
  function move(e) {
    const dx = startX - e.clientX
    chatPanelWidth.value = Math.max(200, Math.min(600, startW + dx))
  }
  function up() {
    document.removeEventListener('mousemove', move)
    document.removeEventListener('mouseup', up)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    saveSizes()
  }
  document.addEventListener('mousemove', move)
  document.addEventListener('mouseup', up)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

async function loadPrompts() {
  loading.value = true
  try {
    prompts.value = await fetchPrompts()
    if (prompts.value.length && !selectedPromptId.value) {
      selectedPromptId.value = prompts.value[0].id
    }
  } catch {
    prompts.value = []
  } finally {
    loading.value = false
  }
}

async function savePrompt({ id, title, content }) {
  try {
    await updatePrompt(id, { title, content })
    const idx = prompts.value.findIndex(p => p.id === id)
    if (idx >= 0) {
      prompts.value[idx] = { ...prompts.value[idx], title, content }
    }
  } catch {
    const idx = prompts.value.findIndex(p => p.id === id)
    if (idx >= 0) {
      prompts.value[idx] = { ...prompts.value[idx], title, content }
    }
  }
}

async function createPrompt() {
  try {
    const prompt = await apiCreate({ title: 'Untitled', content: '' })
    prompts.value.push(prompt)
    selectedPromptId.value = prompt.id
  } catch {}
}

function selectPrompt(id) {
  selectedPromptId.value = id
}

function toggleChatPanel() {
  voicePanelOpen.value = false
  chatPanelOpen.value = !chatPanelOpen.value
}

function toggleVoicePanel() {
  chatPanelOpen.value = false
  voicePanelOpen.value = !voicePanelOpen.value
}

function onApplyEdit(payload) {
  editorRef.value?.applyEdit?.(payload)
}

onMounted(() => {
  loadSizes()
  loadPrompts()
})
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.app-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.app-brand {
  font-size: 15px;
  font-weight: 600;
}

.app-logo {
  color: var(--text-primary);
}

.app-suffix {
  color: var(--text-muted);
  font-weight: 500;
}

.app-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.app-footer .built-by {
  color: var(--text-secondary);
}

.app-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.resize-handle {
  width: 6px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: col-resize;
  background: transparent;
  transition: background var(--transition);
}

.resize-handle:hover {
  background: var(--accent-muted);
}

.resize-line {
  width: 2px;
  height: 100%;
  min-height: 40px;
  background: var(--border);
  border-radius: 1px;
}

.resize-handle:hover .resize-line {
  background: var(--accent);
}
</style>
