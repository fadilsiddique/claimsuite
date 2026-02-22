<template>
  <div class="px-4 py-5">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-xl font-bold text-gray-900">Submit Expense</h2>
      <p class="text-sm text-gray-500 mt-1">Fill in the details for your expense claim</p>
    </div>

    <!-- Form -->
    <div class="space-y-4">
      <!-- Payment Method -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Paid By</label>
        <div class="flex rounded-xl overflow-hidden border-2 border-gray-100">
          <button
            :class="[
              'flex-1 h-11 text-sm font-medium transition-colors',
              form.payment_method === 'employee'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50',
            ]"
            @click="selectPaymentMethod('employee')"
          >
            Me
          </button>
          <button
            :class="[
              'flex-1 h-11 text-sm font-medium transition-colors border-l-2 border-gray-100',
              form.payment_method === 'company'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50',
            ]"
            @click="selectPaymentMethod('company')"
          >
            Company
          </button>
        </div>
      </div>
      <!-- Claim Type -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Claim Type</label>
        <div v-if="settingsResource.loading" class="h-12 rounded-xl bg-gray-100 animate-pulse"></div>
        <select
          v-else
          v-model="form.claim_type"
          class="w-full h-12 px-4 text-sm text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors appearance-none"
        >
          <option value="" disabled>Select claim type</option>
          <option v-for="ct in claimTypes" :key="ct" :value="ct">{{ ct }}</option>
        </select>
      </div>



      <!-- Mode of Payment (only when Company Paid) -->
      <div v-if="form.payment_method === 'company'">
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Mode of Payment</label>
        <div v-if="modesResource.loading" class="h-12 rounded-xl bg-gray-100 animate-pulse"></div>
        <p v-else-if="!modeOptions.length" class="text-sm text-gray-400 py-2">No modes of payment available</p>
        <select
          v-else
          v-model="form.mode_of_payment"
          class="w-full h-12 px-4 text-sm text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors appearance-none"
        >
          <option value="" disabled>Select mode of payment</option>
          <option v-for="m in modeOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <!-- Project -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">
          Project
          <span class="text-gray-400 font-normal">(optional)</span>
        </label>
        <div v-if="projectsResource.loading" class="h-12 rounded-xl bg-gray-100 animate-pulse"></div>
        <p v-else-if="!projectOptions.length" class="text-sm text-gray-400 py-2">No open projects available</p>
        <select
          v-else
          v-model="form.project"
          class="w-full h-12 px-4 text-sm text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors appearance-none"
        >
          <option value="">None</option>
          <option v-for="p in projectOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
        </select>
      </div>

      <!-- Amount -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Amount</label>
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-medium text-gray-400">AED</span>
          <input
            v-model.number="form.amount"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full h-12 pl-14 pr-4 text-lg font-semibold text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors tabular-nums"
          />
        </div>
      </div>

      <!-- Date -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Expense Date</label>
        <input
          type="date"
          v-model="form.expense_date"
          class="w-full h-12 px-4 text-sm text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="What was this expense for?"
          class="w-full px-4 py-3 text-sm text-gray-900 bg-white border-2 border-gray-100 rounded-xl focus:border-gray-900 focus:ring-0 outline-none transition-colors resize-none"
        ></textarea>
      </div>

      <!-- Receipt Upload -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Receipt</label>
        <div
          v-if="!uploadedFile && !isUploading"
          class="relative border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-gray-300 transition-colors cursor-pointer"
          @click="$refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*,.pdf"
            class="hidden"
            @change="handleFileSelect"
          />
          <FeatherIcon name="upload-cloud" class="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-gray-500">
            <span class="font-medium text-gray-700">Tap to upload</span> receipt
          </p>
          <p class="text-xs text-gray-400 mt-1">Image or PDF, max 10MB</p>
        </div>

        <!-- Uploading state -->
        <div
          v-else-if="isUploading"
          class="border-2 border-gray-100 rounded-xl p-4 bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin shrink-0"></div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-700 truncate">Uploading...</p>
            </div>
          </div>
        </div>

        <!-- Uploaded file -->
        <div
          v-else
          class="border-2 border-gray-100 rounded-xl p-4 bg-white"
        >
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-green-50 shrink-0">
              <FeatherIcon name="check-circle" class="w-5 h-5 text-green-600" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ uploadedFile.file_name }}</p>
              <p class="text-xs text-green-600">Uploaded</p>
            </div>
            <button
              @click="removeFile"
              class="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-gray-100 transition-colors shrink-0"
            >
              <FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div
      v-if="form.claim_type && form.amount"
      class="mt-6 bg-gray-50 rounded-2xl p-4 border border-gray-100"
    >
      <p class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Summary</p>
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Type</span>
          <span class="text-sm font-medium text-gray-900">{{ form.claim_type }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Amount</span>
          <span class="text-sm font-bold text-gray-900">AED {{ formattedAmount }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Paid By</span>
          <span class="text-sm text-gray-500">
            {{ form.payment_method === 'company' ? 'Company' : 'Employee' }}
          </span>
        </div>
        <div v-if="form.payment_method === 'company' && form.mode_of_payment" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Mode</span>
          <span class="text-sm text-gray-500">{{ form.mode_of_payment }}</span>
        </div>
        <div v-if="mappedAccount" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Account</span>
          <span class="text-sm text-gray-500">{{ mappedAccount }}</span>
        </div>
        <div v-if="form.project" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Project</span>
          <span class="text-sm text-gray-500">{{ selectedProjectLabel }}</span>
        </div>
        <div v-if="uploadedFile" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Receipt</span>
          <span class="text-sm text-green-600 flex items-center gap-1">
            <FeatherIcon name="paperclip" class="w-3.5 h-3.5" />
            Attached
          </span>
        </div>
      </div>
    </div>

    <!-- Submit Button -->
    <div class="mt-6">
      <button
        class="btn-primary w-full h-12 text-base font-semibold rounded-xl text-white flex items-center justify-center transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="submitResource.loading || !isFormValid || isUploading"
        @click="handleSubmit"
      >
        <span v-if="submitResource.loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></span>
        Submit Claim
      </button>
    </div>
  </div>
</template>

<script>
import { createResource, toast } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'NewClaim',
  components: { FeatherIcon },
  setup() {
    const settingsResource = createResource({
      url: 'claimsuite.api.get_claim_settings',
      auto: true,
    })

    const projectsResource = createResource({
      url: 'claimsuite.api.get_projects',
      auto: true,
    })

    const modesResource = createResource({
      url: 'claimsuite.api.get_modes_of_payment',
      auto: true,
    })

    const submitResource = createResource({
      url: 'claimsuite.api.create_expense_claim',
    })

    return { settingsResource, projectsResource, modesResource, submitResource }
  },
  data() {
    return {
      form: {
        claim_type: '',
        payment_method: 'employee',
        mode_of_payment: '',
        amount: null,
        expense_date: new Date().toISOString().split('T')[0],
        description: '',
        project: '',
      },
      uploadedFile: null,
      isUploading: false,
    }
  },
  computed: {
    claimTypes() {
      return this.settingsResource.data?.claim_types || []
    },
    claimTypeOptions() {
      return this.claimTypes.map(ct => ({ label: ct, value: ct }))
    },
    accountMap() {
      return this.settingsResource.data?.account_map || {}
    },
    mappedAccount() {
      return this.accountMap[this.form.claim_type] || ''
    },
    modeOptions() {
      return this.modesResource.data || []
    },
    projectOptions() {
      return this.projectsResource.data || []
    },
    selectedProjectLabel() {
      const opt = this.projectOptions.find(p => p.value === this.form.project)
      return opt?.label || this.form.project
    },
    formattedAmount() {
      return Number(this.form.amount || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    isFormValid() {
      const base = this.form.claim_type && this.form.amount > 0 && this.form.expense_date
      if (this.form.payment_method === 'company') {
        return base && !!this.form.mode_of_payment
      }
      return base
    },
  },
  methods: {
    selectPaymentMethod(method) {
      this.form.payment_method = method
      if (method === 'employee') {
        this.form.mode_of_payment = ''
      }
    },
    async handleFileSelect(e) {
      const file = e.target.files?.[0]
      if (!file) return

      if (file.size > 10 * 1024 * 1024) {
        toast.error('Maximum file size is 10MB')
        return
      }

      this.isUploading = true
      try {
        const formData = new FormData()
        formData.append('file', file)

        const res = await fetch('/api/method/claimsuite.api.upload_receipt', {
          method: 'POST',
          headers: {
            'X-Frappe-CSRF-Token': window.csrf_token || '',
          },
          body: formData,
        })

        if (!res.ok) throw new Error('Upload failed')

        const data = await res.json()
        this.uploadedFile = data.message
      } catch (err) {
        toast.error('Could not upload the file. Please try again.')
      }
      this.isUploading = false
      e.target.value = ''
    },
    removeFile() {
      this.uploadedFile = null
    },
    async handleSubmit() {
      if (!this.isFormValid) return

      try {
        await this.submitResource.submit({
          claim_type: this.form.claim_type,
          amount: this.form.amount,
          expense_date: this.form.expense_date,
          description: this.form.description,
          file_url: this.uploadedFile?.file_url || '',
          project: this.form.project || '',
          payment_method: this.form.payment_method,
          mode_of_payment: this.form.mode_of_payment || '',
        })

        const result = this.submitResource.data
        if (result?.name) {
          toast.success(`Claim submitted: ${this.form.claim_type} — AED ${this.formattedAmount}`)
          this.$router.push(`/claims/${result.name}`)
        }
      } catch (err) {
        const messages = this.submitResource.error?.messages
        const errorMsg = messages?.length
          ? messages[0]
          : 'Something went wrong. Please try again.'
        toast.error(errorMsg)
      }
    },
  },
}
</script>
