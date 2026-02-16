<template>
  <aside class="sidebar">
    <header class="sidebar-header">
      <h2 class="sidebar-title">Prompts</h2>
      <button class="btn-new" title="New prompt" @click="$emit('create')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        New
      </button>
    </header>
    <div class="prompt-list">
      <button
        v-for="p in prompts"
        :key="p.id"
        class="prompt-card"
        :class="{ selected: selectedId === p.id }"
        @click="$emit('select', p.id)"
      >
        <span class="prompt-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
          </svg>
        </span>
        <span class="prompt-title">{{ p.title || 'Untitled' }}</span>
      </button>
      <div v-if="!prompts.length" class="empty-state">
        <p>No prompts yet</p>
        <button class="btn-empty" @click="$emit('create')">Create prompt</button>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  prompts: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
})

defineEmits(['close', 'select', 'create'])
</script>

<style scoped>
.sidebar {
  min-width: 180px;
  flex-shrink: 0;
  background: var(--bg-elevated);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-new {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition);
}

.btn-new:hover {
  background: var(--accent-hover);
}

.btn-new svg {
  width: 14px;
  height: 14px;
}

.prompt-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.prompt-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition);
}

.prompt-card:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.prompt-card.selected {
  background: var(--accent-muted);
  color: var(--accent);
  font-weight: 500;
}

.prompt-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  flex-shrink: 0;
}

.prompt-card.selected .prompt-icon {
  background: var(--accent-muted);
  color: var(--accent);
}

.prompt-icon svg {
  width: 14px;
  height: 14px;
}

.prompt-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  text-align: center;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.btn-empty {
  padding: 8px 14px;
  background: var(--bg-surface);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition);
}

.btn-empty:hover {
  background: var(--bg-hover);
  color: var(--accent);
  border-color: var(--accent);
}
</style>
