import { ref } from 'vue'

const AUTH_KEY = 'prompt-editor-auth'

export function useAuth() {
  const authenticated = ref(localStorage.getItem(AUTH_KEY) === 'true')

  function login() {
    localStorage.setItem(AUTH_KEY, 'true')
    authenticated.value = true
  }

  function logout() {
    localStorage.removeItem(AUTH_KEY)
    authenticated.value = false
  }

  return {
    authenticated,
    login,
    logout,
  }
}
