const API_BASE = '/api'

// Mock data for when backend is unavailable

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/x/g, () =>
    ((Math.random() * 16) | 0).toString(16)
  )
}

const mockPrompts = [
  {
    id: uuid(),
    title: 'Welcome',
    content: 'Write your first prompt here...',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

let mockStore = [...mockPrompts]

async function request(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
    if (res.status === 204) return null
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data.error || res.statusText)
    return data
  } catch (err) {
    // Fallback to mock when backend unavailable (connection refused, etc.)
    return mockRequest(path, options)
  }
}

function mockRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()

  if (path === '/prompts' && method === 'GET') {
    return Promise.resolve(mockStore.map((p) => ({ ...p })))
  }

  const match = path.match(/^\/prompts\/([^/]+)$/)
  if (match) {
    const id = match[1]
    if (method === 'GET') {
      const p = mockStore.find((x) => x.id === id)
      return p ? Promise.resolve({ ...p }) : Promise.reject(new Error('Not found'))
    }
    if (method === 'PUT') {
      const body = JSON.parse(options.body || '{}')
      const idx = mockStore.findIndex((x) => x.id === id)
      if (idx < 0) return Promise.reject(new Error('Not found'))
      mockStore[idx] = {
        ...mockStore[idx],
        ...body,
        updated_at: new Date().toISOString(),
      }
      return Promise.resolve(mockStore[idx])
    }
    if (method === 'DELETE') {
      mockStore = mockStore.filter((x) => x.id !== id)
      return Promise.resolve(null)
    }
  }

  if (path === '/prompts' && method === 'POST') {
    const body = JSON.parse(options.body || '{}')
    const prompt = {
      id: uuid(),
      title: body.title || 'Untitled',
      content: body.content || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    mockStore.push(prompt)
    return Promise.resolve(prompt)
  }

  return Promise.reject(new Error('Not found'))
}

export async function fetchPrompts() {
  return request('/prompts')
}

export async function fetchPrompt(id) {
  return request(`/prompts/${id}`)
}

export async function createPrompt(body) {
  return request('/prompts', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function updatePrompt(id, body) {
  return request(`/prompts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function deletePrompt(id) {
  return request(`/prompts/${id}`, { method: 'DELETE' })
}
