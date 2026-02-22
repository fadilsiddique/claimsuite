<template>
  <div class="px-4 py-5">
    <!-- Loading -->
    <div v-if="detailResource.loading && !claim" class="space-y-4">
      <div class="bg-white rounded-2xl p-6 border border-gray-100 animate-pulse">
        <div class="h-8 bg-gray-100 rounded w-32 mb-2"></div>
        <div class="h-4 bg-gray-50 rounded w-48"></div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-gray-100 animate-pulse">
        <div class="space-y-4">
          <div v-for="i in 4" :key="i" class="flex justify-between">
            <div class="h-4 bg-gray-100 rounded w-20"></div>
            <div class="h-4 bg-gray-50 rounded w-28"></div>
          </div>
        </div>
      </div>
    </div>

    <template v-else-if="claim">
      <!-- Amount Hero -->
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm mb-4 text-center">
        <div class="flex items-center justify-center gap-2 mb-3">
          <span
            class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
            :class="statusClass"
          >
            {{ statusLabel }}
          </span>
          <span
            v-if="claim.docstatus === 1"
            class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
            :class="paymentStatusClass"
          >
            {{ paymentStatusLabel }}
          </span>
        </div>
        <p class="text-3xl font-bold text-gray-900 tabular-nums">
          AED {{ formattedAmount }}
        </p>
        <p class="text-sm text-gray-500 mt-1">{{ claimType }}</p>
      </div>

      <!-- Details Card -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm mb-4 overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Details</p>
        </div>
        <div class="divide-y divide-gray-50">
          <div class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Reference</span>
            <span class="text-sm font-medium text-gray-900">{{ claim.name }}</span>
          </div>
          <div class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Date</span>
            <span class="text-sm font-medium text-gray-900">{{ formattedDate }}</span>
          </div>
          <div class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Company</span>
            <span class="text-sm font-medium text-gray-900">{{ claim.company }}</span>
          </div>
          <div v-if="claim.project" class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Project</span>
            <span class="text-sm font-medium text-gray-900">{{ claim.project_name || claim.project }}</span>
          </div>
          <div v-if="claim.docstatus === 1" class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Payment</span>
            <span
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold"
              :class="paymentStatusClass"
            >
              {{ paymentStatusLabel }}
            </span>
          </div>
          <div v-if="claim.payment_journal" class="flex items-center justify-between px-4 py-3.5">
            <span class="text-sm text-gray-500">Payment Ref</span>
            <a
              :href="`/app/journal-entry/${claim.payment_journal}`"
              target="_blank"
              class="text-sm font-medium text-blue-600 hover:underline"
            >
              {{ claim.payment_journal }}
            </a>
          </div>
          <div v-if="description" class="px-4 py-3.5">
            <span class="text-sm text-gray-500 block mb-1">Description</span>
            <span class="text-sm text-gray-900">{{ description }}</span>
          </div>
        </div>
      </div>

      <!-- Accounts Card -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm mb-4 overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Account Entries</p>
        </div>
        <div class="divide-y divide-gray-50">
          <div
            v-for="(acc, idx) in claim.accounts"
            :key="idx"
            class="flex items-center justify-between px-4 py-3.5"
          >
            <div class="flex-1 min-w-0 mr-4">
              <p class="text-sm font-medium text-gray-900 truncate">{{ acc.account }}</p>
            </div>
            <div class="text-right shrink-0">
              <p v-if="acc.debit > 0" class="text-sm font-semibold text-red-600 tabular-nums">
                DR {{ formatCurrency(acc.debit) }}
              </p>
              <p v-if="acc.credit > 0" class="text-sm font-semibold text-green-600 tabular-nums">
                CR {{ formatCurrency(acc.credit) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Open in Desk -->
      <a
        :href="`/app/journal-entry/${claim.name}`"
        target="_blank"
        class="flex items-center justify-center gap-2 w-full h-12 bg-white border-2 border-gray-100 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        <FeatherIcon name="external-link" class="w-4 h-4" />
        Open in Desk
      </a>
    </template>

    <!-- Error -->
    <EmptyState
      v-else
      icon="alert-circle"
      title="Claim not found"
      message="This claim may have been deleted or you don't have permission to view it"
    />
  </div>
</template>

<script>
import { createResource } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'ClaimDetail',
  components: { FeatherIcon, EmptyState },
  setup() {
    const detailResource = createResource({
      url: 'claimsuite.api.get_claim_detail',
    })
    return { detailResource }
  },
  computed: {
    claim() {
      return this.detailResource.data
    },
    claimType() {
      return this.parseRemark().type || 'Expense Claim'
    },
    description() {
      return this.parseRemark().description || ''
    },
    formattedAmount() {
      return Number(this.claim?.total_debit || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    formattedDate() {
      if (!this.claim?.posting_date) return ''
      const d = new Date(this.claim.posting_date)
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
    },
    statusLabel() {
      if (this.claim?.docstatus === 0) return 'Draft'
      if (this.claim?.docstatus === 1) return 'Submitted'
      return 'Cancelled'
    },
    statusClass() {
      if (this.claim?.docstatus === 0) return 'bg-gray-100 text-gray-700'
      if (this.claim?.docstatus === 1) return 'bg-blue-50 text-blue-700'
      return 'bg-red-50 text-red-600'
    },
    paymentStatusLabel() {
      return this.claim?.payment_status === 'Paid' ? 'Paid' : 'Pending'
    },
    paymentStatusClass() {
      return this.claim?.payment_status === 'Paid'
        ? 'bg-green-50 text-green-700'
        : 'bg-amber-50 text-amber-700'
    },
  },
  mounted() {
    this.fetchDetail()
    window.addEventListener('app:refresh', this._onRefresh)
  },
  beforeUnmount() {
    window.removeEventListener('app:refresh', this._onRefresh)
  },
  methods: {
    _onRefresh() {
      this.fetchDetail()
    },
    fetchDetail() {
      const name = this.$route.params.name
      if (name) {
        this.detailResource.submit({ name })
      }
    },
    parseRemark() {
      const remark = this.claim?.user_remark || ''
      const match = remark.match(/^Expense Claim - (.+?) - (.*?) - (.+)$/)
      if (match) {
        return { type: match[1], description: match[2], date: match[3] }
      }
      return {}
    },
    formatCurrency(val) {
      return Number(val).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
  },
}
</script>
