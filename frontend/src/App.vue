<template>
  <FrappeUIProvider>
    <!-- Auth loading splash -->
    <div
      v-if="isLoading"
      class="fixed inset-0 flex flex-col items-center justify-center gap-4"
      style="background: linear-gradient(150deg, #29A38B 0%, #1e8a74 100%)"
    >
      <div
        class="w-16 h-16 rounded-2xl flex items-center justify-center mb-2 shadow-lg"
        style="background: rgba(255,255,255,0.2)"
      >
        <FeatherIcon name="file-text" class="w-8 h-8 text-white" />
      </div>
      <p class="text-white text-xl font-bold tracking-tight">ClaimSuite</p>
      <div class="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mt-2"></div>
    </div>

    <!-- Not logged in -->
    <Login v-else-if="!isLoggedIn" />

    <!-- Logged in -->
    <AppShell v-else />
  </FrappeUIProvider>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { FrappeUIProvider } from 'frappe-ui'
import AppShell from '@/components/AppShell.vue'
import Login from '@/pages/Login.vue'
import { useAuth } from '@/composables/useAuth'
import { useInstallPrompt } from '@/composables/useInstallPrompt'

export default {
  name: 'App',
  components: { AppShell, FrappeUIProvider, Login, FeatherIcon },
  setup() {
    const { isLoggedIn, isLoading, init } = useAuth()
    const { init: initInstallPrompt } = useInstallPrompt()

    // Register beforeinstallprompt listener as early as possible
    initInstallPrompt()

    // Check session
    init()

    return { isLoggedIn, isLoading }
  },
}
</script>
