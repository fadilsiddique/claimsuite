import { ref } from 'vue'

const user = ref('Administrator')
const userInfo = ref({ name: 'Administrator', full_name: 'Administrator', user_image: null })
const isLoggedIn = ref(true)
const isLoading = ref(false)

export function useAuth() {
  async function init() {
    // Auth check disabled for now
  }

  function logout() {
    window.location.href = '/api/method/logout'
  }

  return {
    user,
    userInfo,
    isLoggedIn,
    isLoading,
    init,
    logout,
  }
}
