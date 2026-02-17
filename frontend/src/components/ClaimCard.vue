<template>
  <router-link
    :to="`/claims/${claim.name}`"
    class="block bg-white rounded-2xl p-4 border border-gray-100 shadow-sm active:scale-[0.98] transition-transform duration-100"
  >
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0 flex-1">
        <div
          class="flex items-center justify-center w-10 h-10 rounded-xl shrink-0"
          :class="typeIconBg"
        >
          <FeatherIcon :name="typeIcon" class="w-5 h-5" :class="typeIconColor" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-gray-900 truncate">{{ claimType }}</p>
          <p class="text-xs text-gray-500 truncate mt-0.5">{{ description }}</p>
        </div>
      </div>
      <div class="text-right shrink-0">
        <p class="text-sm font-bold text-gray-900 tabular-nums">AED {{ formattedAmount }}</p>
        <div class="flex items-center justify-end gap-1.5 mt-1">
          <span
            class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold"
            :class="statusClass"
          >
            {{ statusLabel }}
          </span>
        </div>
      </div>
    </div>
    <div class="flex items-center gap-2 mt-3 pt-3 border-t border-gray-50">
      <FeatherIcon name="calendar" class="w-3.5 h-3.5 text-gray-400" />
      <span class="text-xs text-gray-400">{{ formattedDate }}</span>
    </div>
  </router-link>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

const TYPE_ICONS = {
  Food: 'coffee',
  Telephone: 'phone',
  Travel: 'map-pin',
  Transport: 'truck',
  Accommodation: 'home',
  Entertainment: 'music',
  Office: 'briefcase',
}

export default {
  name: 'ClaimCard',
  components: { FeatherIcon },
  props: {
    claim: { type: Object, required: true },
  },
  computed: {
    claimType() {
      return this.parseRemark().type || 'Expense'
    },
    description() {
      return this.parseRemark().description || this.claim.name
    },
    typeIcon() {
      return TYPE_ICONS[this.claimType] || 'file-text'
    },
    typeIconBg() {
      return this.claim.docstatus === 1 ? 'bg-green-50' : 'bg-gray-100'
    },
    typeIconColor() {
      return this.claim.docstatus === 1 ? 'text-green-600' : 'text-gray-500'
    },
    formattedAmount() {
      return Number(this.claim.total_debit || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    formattedDate() {
      if (!this.claim.posting_date) return ''
      const d = new Date(this.claim.posting_date)
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    statusLabel() {
      if (this.claim.docstatus === 0) return 'Draft'
      if (this.claim.docstatus === 1) return 'Submitted'
      return 'Cancelled'
    },
    statusClass() {
      if (this.claim.docstatus === 0) return 'bg-gray-100 text-gray-600'
      if (this.claim.docstatus === 1) return 'bg-blue-50 text-blue-700'
      return 'bg-red-50 text-red-600'
    },
  },
  methods: {
    parseRemark() {
      const remark = this.claim.user_remark || ''
      const match = remark.match(/^Expense Claim - (.+?) - (.+?) - (.+)$/)
      if (match) {
        return { type: match[1], description: match[2], date: match[3] }
      }
      return {}
    },
  },
}
</script>
