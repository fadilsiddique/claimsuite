import { ref, computed } from 'vue'

const deferredPrompt = ref(null)
const isInstalled = ref(window.matchMedia('(display-mode: standalone)').matches)
const _dismissed = ref(localStorage.getItem('cs-pwa-dismissed') === 'true')

let _initialized = false

export function useInstallPrompt() {
  const canInstall = computed(
    () => !!deferredPrompt.value && !_dismissed.value && !isInstalled.value,
  )

  function init() {
    if (_initialized || isInstalled.value) return
    _initialized = true

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      deferredPrompt.value = e
    })

    window.addEventListener('appinstalled', () => {
      deferredPrompt.value = null
      isInstalled.value = true
    })
  }

  async function install() {
    if (!deferredPrompt.value) return
    deferredPrompt.value.prompt()
    const { outcome } = await deferredPrompt.value.userChoice
    deferredPrompt.value = null
    if (outcome === 'accepted') isInstalled.value = true
  }

  function dismiss() {
    _dismissed.value = true
    localStorage.setItem('cs-pwa-dismissed', 'true')
  }

  return { canInstall, isInstalled, init, install, dismiss }
}
