<template>
  <div class="flex flex-col items-center justify-center py-12 px-6">
    <div class="flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 mb-4">
      <FeatherIcon :name="icon" class="w-7 h-7 text-gray-400" />
    </div>
    <p class="text-base font-semibold text-gray-900 text-center">{{ title }}</p>
    <p class="text-sm text-gray-500 text-center mt-1 max-w-[240px]">{{ message }}</p>
    <slot name="action" />
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'EmptyState',
  components: { FeatherIcon },
  props: {
    icon: { type: String, default: 'inbox' },
    title: { type: String, default: 'Nothing here yet' },
    message: { type: String, default: '' },
  },
}
</script>
