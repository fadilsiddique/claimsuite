import { ref } from 'vue'

const user = ref(null)
const userInfo = ref(null)
const isLoggedIn = ref(false)
const isLoading = ref(true)

let _initPromise = null

export function useAuth() {
  async function init() {
    if (_initPromise) return _initPromise
    _initPromise = _doInit()
    return _initPromise
  }

  async function _doInit() {
    isLoading.value = true
    try {
      const res = await fetch('/api/method/frappe.auth.get_logged_user', {
        credentials: 'same-origin',
      })
      if (res.ok) {
        const data = await res.json()
        const loggedUser = data.message
        if (loggedUser && loggedUser !== 'Guest') {
          user.value = loggedUser
          isLoggedIn.value = true
          await _fetchUserInfo(loggedUser)
        } else {
          isLoggedIn.value = false
        }
      } else {
        isLoggedIn.value = false
      }
    } catch {
      isLoggedIn.value = false
    } finally {
      isLoading.value = false
    }
  }

  async function _fetchUserInfo(email) {
    try {
      const res = await fetch(
        `/api/resource/User/${encodeURIComponent(email)}?fields=["full_name","user_image"]`,
        { credentials: 'same-origin' },
      )
      const data = await res.json()
      userInfo.value = data.data || {}
    } catch {
      userInfo.value = { full_name: email, user_image: null }
    }
  }

  async function login(usr, pwd) {
    const body = new URLSearchParams({ usr, pwd })
    const res = await fetch('/api/method/login', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    })

    const data = await res.json()

    if (!res.ok) {
      let msg = 'Invalid credentials. Please try again.'
      if (data._server_messages) {
        try {
          msg = JSON.parse(JSON.parse(data._server_messages)[0]).message
        } catch {}
      }
      throw new Error(msg)
    }

    // Reset and re-init to get fresh session
    _initPromise = null
    user.value = usr
    isLoggedIn.value = true
    await _fetchUserInfo(usr)
    isLoading.value = false

    if (data.csrf_token) window.csrf_token = data.csrf_token
  }

  async function logout() {
    try {
      await fetch('/api/method/logout', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-Frappe-CSRF-Token': window.csrf_token || 'fetch' },
      })
    } catch {}
    isLoggedIn.value = false
    user.value = null
    userInfo.value = null
    _initPromise = null
    // Hard reload so Frappe clears the session cookie cleanly
    window.location.reload()
  }

  return { user, userInfo, isLoggedIn, isLoading, init, login, logout }
}
