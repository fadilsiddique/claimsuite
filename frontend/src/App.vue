<template>
  <FrappeUIProvider>
    <AppShell />
  </FrappeUIProvider>
</template>

<script>
import AppShell from '@/components/AppShell.vue'
import { FrappeUIProvider } from 'frappe-ui'

export default {
  name: 'App',
  components: { AppShell, FrappeUIProvider },
}
</script>
