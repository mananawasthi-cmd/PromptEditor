/**
 * Stream chat completion from backend. Yields { content } or { error }.
 */
export async function* streamChat({ promptContent, selectedText, message, messages: history }) {
  let res
  try {
    res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt_content: promptContent || '',
        selected_text: selectedText || '',
        message: message || '',
        messages: history || [],
      }),
    })
  } catch (e) {
    yield { error: 'Cannot reach server. Is the backend running?' }
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    yield { error: err.error || res.statusText }
    return
  }

  const reader = res.body?.getReader()
  if (!reader) {
    yield { error: 'No response body' }
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''
      for (const part of parts) {
        const line = part.trim()
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.content) yield { content: data.content }
            if (data.error) yield { error: data.error }
          } catch (_) {}
        }
      }
    }
  } catch (e) {
    yield { error: e.message || 'Stream error' }
  }
}

/** Voice chat: speak about your pitch, get AI response. Same stream format. */
export async function* streamVoiceChat({ promptContent, message, messages: history }) {
  let res
  try {
    res = await fetch('/api/voice-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt_content: promptContent || '',
        message: message || '',
        messages: history || [],
      }),
    })
  } catch (e) {
    yield { error: 'Cannot reach server. Is the backend running?' }
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    yield { error: err.error || res.statusText }
    return
  }

  const reader = res.body?.getReader()
  if (!reader) {
    yield { error: 'No response body' }
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''
      for (const part of parts) {
        const line = part.trim()
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.content) yield { content: data.content }
            if (data.error) yield { error: data.error }
          } catch (_) {}
        }
      }
    }
  } catch (e) {
    yield { error: e.message || 'Stream error' }
  }
}
