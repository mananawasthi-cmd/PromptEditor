<template>
  <div class="settings-wrap" ref="wrapRef">
    <button class="settings-btn" title="Voice settings" @click="open = !open">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
      </svg>
    </button>
    <div v-if="open" class="settings-dropdown" @click.stop>
      <div class="settings-section">
        <label class="settings-label">TTS Voice ID</label>
        <input
          v-model="voiceId"
          class="settings-input"
          placeholder="ElevenLabs voice ID"
        />
        <label class="settings-label">Voice Speed</label>
        <div class="speed-wrap">
          <input
            v-model.number="voiceSpeed"
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            class="speed-slider"
          />
          <span class="speed-value">{{ voiceSpeed.toFixed(1) }}x</span>
        </div>
        <p class="settings-hint">Set once to listen. Speed: 1.0 = normal. Get IDs from elevenlabs.io</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useTtsSettings } from '../composables/useTtsSettings'

const { voiceId, voiceSpeed, openSettings } = useTtsSettings()
const open = ref(false)
const wrapRef = ref(null)

watch(openSettings, (v) => {
  if (v) {
    open.value = true
    openSettings.value = false
  }
})

function onClickOutside(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.settings-wrap {
  position: relative;
}

.settings-btn {
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

.settings-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.settings-btn svg {
  width: 18px;
  height: 18px;
}

.settings-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 280px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.settings-input {
  padding: 8px 12px;
  background: var(--bg-base);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
  outline: none;
  transition: border-color var(--transition);
}

.settings-input:focus {
  border-color: var(--accent);
}

.settings-input::placeholder {
  color: var(--text-muted);
}

.settings-hint {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

.speed-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-base);
  border-radius: 3px;
  outline: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: var(--accent);
  border-radius: 50%;
  cursor: pointer;
}

.speed-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 36px;
}
</style>
