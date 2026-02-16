import { ref, readonly } from 'vue'

const chatContextRef = ref({
  promptContent: '',
  selectedText: '',
  selectionStart: 0,
  selectionEnd: 0,
})

export function useChatContext() {
  function setContext({ promptContent = '', selectedText = '', selectionStart = 0, selectionEnd = 0 }) {
    chatContextRef.value = {
      promptContent,
      selectedText,
      selectionStart,
      selectionEnd,
    }
  }

  return {
    chatContext: readonly(chatContextRef),
    setChatContext: setContext,
  }
}
