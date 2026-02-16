<template>
  <aside class="activity-bar">
    <div class="activity-brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
        </svg>
      </div>
    </div>
    <nav class="activity-nav">
      <button
        class="activity-btn"
        :class="{ active: activeView === 'prompts' }"
        title="Prompts"
        @click="$emit('view-change', 'prompts')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
      </button>
      <button
        class="activity-btn"
        :class="{ active: chatPanelOpen }"
        title="Chat"
        @click="$emit('chat-panel-toggle')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>
      <button
        class="activity-btn"
        :class="{ active: voicePanelOpen }"
        title="Voice Chat"
        @click="$emit('voice-panel-toggle')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="22" />
        </svg>
      </button>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  activeView: String,
  chatPanelOpen: Boolean,
  voicePanelOpen: Boolean,
})

defineEmits(['view-change', 'chat-panel-toggle', 'voice-panel-toggle'])
</script>

<style scoped>
.activity-bar {
  width: var(--sidebar-width);
  background: var(--bg-elevated);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
  gap: 4px;
}

.activity-brand {
  margin-bottom: 8px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  border-radius: var(--radius-md);
  color: white;
  transition: background var(--transition);
}

.brand-icon:hover {
  background: var(--accent-hover);
}

.brand-icon svg {
  width: 18px;
  height: 18px;
}

.activity-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition);
}

.activity-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.activity-btn.active {
  color: var(--accent);
  background: var(--accent-muted);
}

.activity-btn svg {
  width: 20px;
  height: 20px;
}
</style>
