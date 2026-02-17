<template>
  <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
    <div class="flex items-center gap-3">
      <div
        class="flex items-center justify-center w-10 h-10 rounded-xl"
        :class="iconBgClass"
      >
        <FeatherIcon :name="icon" class="w-5 h-5" :class="iconClass" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-2xl font-bold text-gray-900 tabular-nums">{{ displayValue }}</p>
        <p class="text-xs font-medium text-gray-500 truncate">{{ label }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'StatCard',
  components: { FeatherIcon },
  props: {
    label: { type: String, required: true },
    value: { type: [Number, String], default: 0 },
    icon: { type: String, default: 'activity' },
    color: { type: String, default: 'gray' },
    isCurrency: { type: Boolean, default: false },
  },
  computed: {
    displayValue() {
      if (this.isCurrency) {
        return `AED ${Number(this.value).toLocaleString('en-AE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      }
      return this.value
    },
    iconBgClass() {
      const map = {
        blue: 'bg-blue-50',
        green: 'bg-green-50',
        amber: 'bg-amber-50',
        gray: 'bg-gray-100',
        red: 'bg-red-50',
      }
      return map[this.color] || map.gray
    },
    iconClass() {
      const map = {
        blue: 'text-blue-600',
        green: 'text-green-600',
        amber: 'text-amber-600',
        gray: 'text-gray-600',
        red: 'text-red-600',
      }
      return map[this.color] || map.gray
    },
  },
}
</script>
