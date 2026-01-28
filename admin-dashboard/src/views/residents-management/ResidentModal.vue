<script setup>
import { ref, watch, computed } from 'vue'
import { 
  NModal, 
  NCard, 
  NInput, 
  NButton, 
  NSwitch,
  NSelect,
  NCollapse,
  NCollapseItem,
  NDataTable
} from 'naive-ui'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'add', // 'add' or 'view'
    validator: (value) => ['add', 'view'].includes(value)
  },
  resident: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

// Form data
const formData = ref({
  firstName: '',
  middleName: '',
  lastName: '',
  suffix: '',
  rfid: '',
  status: true,
  phoneNumber: '',
  email: '',
  houseNo: '',
  purok: ''
})

// Suffix options
const suffixOptions = [
  { label: 'None', value: '' },
  { label: 'Jr.', value: 'Jr.' },
  { label: 'Sr.', value: 'Sr.' },
  { label: 'II', value: 'II' },
  { label: 'III', value: 'III' },
  { label: 'IV', value: 'IV' }
]

// Purok options (adjust based on your needs)
const purokOptions = Array.from({ length: 10 }, (_, i) => ({
  label: `Purok ${i + 1}`,
  value: `Purok ${i + 1}`
}))

// Transaction history (mock data)
const transactionHistory = ref([
  {
    transactionNumber: 'DR-1203',
    request: 'RFID Card',
    createdOn: '12/12/12',
    status: 'Completed'
  },
  {
    transactionNumber: 'EB-1239',
    request: '2x Event Tent, 1x Sound System, 1x Folding Tables',
    createdOn: '12/12/12',
    status: 'Returned'
  }
])

const transactionColumns = [
  {
    title: 'Transaction Number',
    key: 'transactionNumber',
    width: 180
  },
  {
    title: 'Request',
    key: 'request'
  },
  {
    title: 'Created on',
    key: 'createdOn',
    width: 120
  },
  {
    title: 'Status',
    key: 'status',
    width: 120,
    render(row) {
      const statusClass = row.status === 'Completed' 
        ? 'bg-green-100 text-green-800' 
        : 'bg-yellow-100 text-yellow-800'
      return `<span class="px-3 py-1 rounded-full text-xs font-medium ${statusClass}">${row.status}</span>`
    }
  }
]

// Modal title
const modalTitle = computed(() => {
  if (props.mode === 'add') return 'Register New Resident'
  if (formData.value.firstName && formData.value.lastName) {
    return `${formData.value.firstName} ${formData.value.middleName} ${formData.value.lastName} ${formData.value.suffix}`.trim()
  }
  return 'Resident Details'
})

// Watch for prop changes
watch(() => props.show, (newVal) => {
  if (newVal && props.resident) {
    // Populate form with resident data
    formData.value = {
      firstName: props.resident.firstName || '',
      middleName: props.resident.middleName || '',
      lastName: props.resident.lastName || '',
      suffix: props.resident.suffix || '',
      rfid: props.resident.rfid || '',
      status: props.resident.status === 'Active',
      phoneNumber: props.resident.phoneNumber || '',
      email: props.resident.email || '',
      houseNo: props.resident.houseNo || '',
      purok: props.resident.purok || ''
    }
  } else if (newVal && props.mode === 'add') {
    // Reset form for new resident
    formData.value = {
      firstName: '',
      middleName: '',
      lastName: '',
      suffix: '',
      rfid: '',
      status: true,
      phoneNumber: '',
      email: '',
      houseNo: '',
      purok: ''
    }
  }
})

function handleSave() {
  emit('save', {
    ...formData.value,
    status: formData.value.status ? 'Active' : 'Inactive'
  })
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <NModal
    :show="show"
    @update:show="handleClose"
    :mask-closable="false"
  >
    <NCard
      style="width: 800px; max-height: 90vh; overflow-y: auto;"
      :title="modalTitle"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <template #header-extra>
        <button
          @click="handleClose"
          class="p-1 hover:bg-gray-100 rounded transition"
        >
          <XMarkIcon class="w-6 h-6 text-gray-500" />
        </button>
      </template>

      <!-- Personal Information Section -->
      <div class="space-y-4 mb-6">
        <!-- Name Fields -->
        <div class="grid grid-cols-4 gap-4">
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">First Name</label>
            <NInput
              v-model:value="formData.firstName"
              placeholder="First Name"
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Middle Name</label>
            <NInput
              v-model:value="formData.middleName"
              placeholder="Middle Name"
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Surname</label>
            <NInput
              v-model:value="formData.lastName"
              placeholder="Surname"
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Suffix</label>
            <NSelect
              v-model:value="formData.suffix"
              :options="suffixOptions"
              placeholder="Suffix"
              :disabled="mode === 'view'"
            />
          </div>
        </div>

        <!-- RFID, Status, Phone, Email -->
        <div class="grid grid-cols-4 gap-4">
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">RFID No.</label>
            <NInput
              v-model:value="formData.rfid"
              placeholder="RFID No."
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Status</label>
            <div class="flex items-center gap-2 mt-2">
              <NSwitch 
                v-model:value="formData.status"
                :disabled="mode === 'view'"
              />
              <span class="text-sm text-gray-700">
                {{ formData.status ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Phone Number</label>
            <NInput
              v-model:value="formData.phoneNumber"
              placeholder="Phone Number"
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Email</label>
            <NInput
              v-model:value="formData.email"
              placeholder="Email"
              :disabled="mode === 'view'"
            />
          </div>
        </div>

        <!-- Address Fields -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">House No./St.</label>
            <NInput
              v-model:value="formData.houseNo"
              placeholder="House No./St."
              :disabled="mode === 'view'"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1.5">Purok</label>
            <NSelect
              v-model:value="formData.purok"
              :options="purokOptions"
              placeholder="Select Purok"
              :disabled="mode === 'view'"
            />
          </div>
        </div>
      </div>

      <!-- Transaction History (only in view mode) -->
      <div v-if="mode === 'view'" class="mt-6">
        <NCollapse>
          <NCollapseItem title="Transaction History" name="transactions">
            <NDataTable
              :columns="transactionColumns"
              :data="transactionHistory"
              :bordered="false"
              size="small"
            />
          </NCollapseItem>
        </NCollapse>
      </div>

      <!-- Action Buttons -->
      <template #footer>
        <div class="flex justify-end gap-3">
          <NButton @click="handleClose">
            {{ mode === 'view' ? 'Close' : 'Cancel' }}
          </NButton>
          <NButton 
            v-if="mode === 'add'"
            type="primary" 
            @click="handleSave"
          >
            Save
          </NButton>
          <NButton 
            v-if="mode === 'view'"
            type="primary" 
            @click="handleSave"
          >
            Update
          </NButton>
        </div>
      </template>
    </NCard>
  </NModal>
</template>

<style scoped>
:deep(.n-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.n-card__content) {
  padding: 24px;
}

:deep(.n-card__footer) {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
}

:deep(.n-collapse .n-collapse-item__header) {
  font-weight: 600;
  padding: 12px 0;
}
</style>