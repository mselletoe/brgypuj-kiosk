<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { 
  NModal,
  NInput, 
  NButton, 
  NSwitch,
  NSelect,
  NCollapse,
  NCollapseItem,
  NDataTable,
  NDatePicker,
  NSpin,
  useMessage
} from 'naive-ui'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { 
  fetchResidentDetail, 
  createResident, 
  updateResident,
  updateResidentAddress,
  updateResidentRFID,
  fetchPuroks 
} from '@/api/residentService'
import { fetchResidentTransactionHistory } from '@/api/transactionService'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'add',
    validator: (value) => ['add', 'view'].includes(value)
  },
  residentId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])
const message = useMessage()
const originalFormData = ref(null)

function normalizeForm(data) {
  return JSON.stringify({
    ...data,
    birthdate: data.birthdate ? Number(data.birthdate) : null,
    residency_start_date: data.residency_start_date
      ? Number(data.residency_start_date)
      : null
  })
}

const isFormChanged = computed(() => {
  if (!originalFormData.value) return false
  return normalizeForm(formData.value) !== normalizeForm(originalFormData.value)
})


// Loading states
const loading = ref(false)
const saving = ref(false)

// Resident details (for view mode)
const residentDetails = ref(null)

// Form data
const formData = ref({
  // Personal Info
  first_name: '',
  middle_name: '',
  last_name: '',
  suffix: '',
  gender: 'male',
  birthdate: null,
  
  // Contact Info
  phone_number: '',
  email: '',
  
  // Residency Info
  residency_start_date: null,
  
  // Address Info
  house_no_street: '',
  purok_id: null,
  barangay: 'Poblacion Uno',
  municipality: 'Amadeo',
  province: 'Cavite',
  region: 'Region IV-A',
  
  // RFID Info
  rfid_uid: '',
  is_active: true
})

// Dropdown options
const suffixOptions = [
  { label: 'None', value: '' },
  { label: 'Jr.', value: 'Jr.' },
  { label: 'Sr.', value: 'Sr.' },
  { label: 'II', value: 'II' },
  { label: 'III', value: 'III' },
  { label: 'IV', value: 'IV' }
]

const genderOptions = [
  { label: 'Male', value: 'male' },
  { label: 'Female', value: 'female' },
  { label: 'Other', value: 'other' }
]

const purokOptions = ref([])

// Transaction history (only loaded in view mode)
const transactionHistory = ref([])
const transactionLoading = ref(false)

const transactionColumns = [
  {
    title: 'Transaction No.',
    key: 'transaction_no',
    width: 160
  },
  {
    title: 'Type',
    key: 'transaction_type',
    width: 110,
    render(row) {
      const map = { document: 'Document', equipment: 'Equipment', rfid: 'RFID' }
      return map[row.transaction_type] ?? row.transaction_type
    }
  },
  {
    title: 'Request',
    key: 'transaction_name'
  },
  {
    title: 'Created On',
    key: 'created_at',
    width: 130,
    render(row) {
      return new Date(row.created_at).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    }
  },
  {
    title: 'Status',
    key: 'status',
    width: 110
  }
]

async function loadTransactionHistory() {
  transactionLoading.value = true
  try {
    transactionHistory.value = await fetchResidentTransactionHistory(props.residentId)
  } catch (error) {
    console.error('Failed to load transaction history:', error)
    message.error('Failed to load transaction history')
  } finally {
    transactionLoading.value = false
  }
}

// Modal title
const modalTitle = computed(() => {
  if (props.mode === 'add') return 'Register New Resident'
  if (residentDetails.value) {
    return residentDetails.value.full_name
  }
  return 'Resident Details'
})

// Load puroks on mount
onMounted(async () => {
  try {
    const data = await fetchPuroks()
    purokOptions.value = data.map(p => ({
      label: p.purok_name,
      value: p.id
    }))
  } catch (error) {
    console.error('Failed to load puroks:', error)
    message.error('Failed to load puroks')
  }
})

// Load resident details when modal opens in view mode
watch(() => props.show, async (newVal) => {
  if (newVal) {
    if (props.mode === 'view' && props.residentId) {
      // Load resident details and transaction history
      await loadResidentDetails()
      await loadTransactionHistory()
    } else if (props.mode === 'add') {
      // Reset transaction history for clean state
      transactionHistory.value = []
      // Reset form for new resident
      resetForm()
    }
  }
})

async function loadResidentDetails() {
  loading.value = true
  try {
    const data = await fetchResidentDetail(props.residentId)
    residentDetails.value = data
    
    // Populate form data for editing
    formData.value = {
      first_name: data.first_name,
      middle_name: data.middle_name || '',
      last_name: data.last_name,
      suffix: data.suffix || '',
      gender: data.gender,
      birthdate: data.birthdate, // Already formatted as MM/DD/YYYY
      phone_number: data.phone_number || '',
      email: data.email || '',
      residency_start_date: data.residency_start_date,
      house_no_street: data.current_address?.house_no_street || '',
      purok_id: data.current_address?.purok_id || null,
      barangay: data.current_address?.barangay || 'Poblacion Uno',
      municipality: data.current_address?.municipality || 'Amadeo',
      province: data.current_address?.province || 'Cavite',
      region: data.current_address?.region || 'Region IV-A',
      rfid_uid: data.active_rfid?.rfid_uid || '',
      is_active: data.active_rfid?.is_active ?? true
    }

    originalFormData.value = JSON.parse(JSON.stringify(formData.value))

  } catch (error) {
    console.error('Failed to load resident details:', error)
    message.error('Failed to load resident details')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  const today = new Date()
  formData.value = {
    first_name: '',
    middle_name: '',
    last_name: '',
    suffix: '',
    gender: 'male',
    birthdate: null,
    phone_number: '',
    email: '',
    residency_start_date: today.getTime(),
    house_no_street: '',
    purok_id: null,
    barangay: 'Poblacion Uno',
    municipality: 'Amadeo',
    province: 'Cavite',
    region: 'Region IV-A',
    rfid_uid: '',
    is_active: true
  }

  originalFormData.value = JSON.parse(JSON.stringify(formData.value))
}

// Convert timestamp to YYYY-MM-DD format
function formatDateForAPI(timestamp) {
  if (!timestamp) return null
  const date = new Date(timestamp)
  return date.toISOString().split('T')[0]
}

async function handleSave() {
  // Validation
  if (!formData.value.first_name || !formData.value.last_name) {
    message.error('First name and last name are required')
    return
  }
  
  if (!formData.value.birthdate) {
    message.error('Birthdate is required')
    return
  }
  
  if (props.mode === 'add') {
    if (!formData.value.house_no_street || !formData.value.purok_id) {
      message.error('House/Street and Purok are required')
      return
    }
    
    if (!formData.value.rfid_uid) {
      message.error('RFID No. is required')
      return
    }
  }
  
  saving.value = true
  
  try {
    if (props.mode === 'add') {
      // Create new resident
      const payload = {
        first_name: formData.value.first_name,
        middle_name: formData.value.middle_name || null,
        last_name: formData.value.last_name,
        suffix: formData.value.suffix || null,
        gender: formData.value.gender,
        birthdate: formatDateForAPI(formData.value.birthdate),
        email: formData.value.email || null,
        phone_number: formData.value.phone_number || null,
        residency_start_date: formatDateForAPI(formData.value.residency_start_date),
        address: {
          house_no_street: formData.value.house_no_street,
          purok_id: formData.value.purok_id,
          barangay: formData.value.barangay,
          municipality: formData.value.municipality,
          province: formData.value.province,
          region: formData.value.region
        },
        rfid: {
          rfid_uid: formData.value.rfid_uid,
          is_active: formData.value.is_active
        }
      }
      
      await createResident(payload)
      message.success('Resident registered successfully')
    } else {
      // Update existing resident
      // Update basic info
      await updateResident(props.residentId, {
        first_name: formData.value.first_name,
        middle_name: formData.value.middle_name || null,
        last_name: formData.value.last_name,
        suffix: formData.value.suffix || null,
        gender: formData.value.gender,
        email: formData.value.email || null,
        phone_number: formData.value.phone_number || null
      })
      
      // Update address if changed
      if (formData.value.house_no_street || formData.value.purok_id) {
        await updateResidentAddress(props.residentId, {
          house_no_street: formData.value.house_no_street,
          purok_id: formData.value.purok_id,
          barangay: formData.value.barangay,
          municipality: formData.value.municipality,
          province: formData.value.province,
          region: formData.value.region
        })
      }
      
      // Update RFID if changed
      if (formData.value.rfid_uid) {
        await updateResidentRFID(props.residentId, {
          rfid_uid: formData.value.rfid_uid,
          is_active: formData.value.is_active
        })
      }
      
      message.success('Resident updated successfully')
    }
    
    emit('saved')
  } catch (error) {
    console.error('Failed to save resident:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to save resident'
    message.error(errorMsg)
  } finally {
    saving.value = false
  }
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
    <div
      class="w-[900px] max-h-[90vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col"
      role="dialog"
      aria-modal="true"
    >
      <!-- HEADER -->
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-semibold text-gray-800">
          {{ modalTitle }}
        </h2>

        <button
          @click="handleClose"
          class="p-1 rounded hover:bg-gray-100 transition"
        >
          <XMarkIcon class="w-6 h-6 text-gray-500" />
        </button>
      </div>

      <!-- LOADING STATE -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <NSpin size="large" />
      </div>

      <!-- CONTENT -->
      <div v-else class="px-6 py-6 space-y-6 overflow-y-auto">
        <!-- ADD/EDIT MODE - Form -->
        <div class="space-y-4">
          <!-- Name Fields -->
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                First Name <span class="text-red-500">*</span>
              </label>
              <NInput v-model:value="formData.first_name" placeholder="First Name" />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">Middle Name</label>
              <NInput v-model:value="formData.middle_name" placeholder="Middle Name" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Last Name <span class="text-red-500">*</span>
              </label>
              <NInput v-model:value="formData.last_name" placeholder="Last Name" />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">Suffix</label>
              <NSelect
                v-model:value="formData.suffix"
                :options="suffixOptions"
                placeholder="Select Suffix"
              />
            </div>
          </div>

          <!-- Gender, Birthdate, Residency Start -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Gender <span class="text-red-500">*</span>
              </label>
              <NSelect
                v-model:value="formData.gender"
                :options="genderOptions"
                placeholder="Select Gender"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Birthdate <span class="text-red-500">*</span>
              </label>
              <NDatePicker
                v-model:value="formData.birthdate"
                type="date"
                placeholder="Select Birthdate"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">Residency Start Date</label>
              <NDatePicker
                v-model:value="formData.residency_start_date"
                type="date"
                placeholder="Select Date"
                class="w-full"
              />
            </div>
          </div>

          <!-- Contact Information -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">Phone Number</label>
              <NInput v-model:value="formData.phone_number" placeholder="09123456789" />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">Email</label>
              <NInput v-model:value="formData.email" type="email" placeholder="email@example.com" />
            </div>
          </div>

          <!-- Address -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                House No./Blk/Street <span v-if="mode === 'add'" class="text-red-500">*</span>
              </label>
              <NInput v-model:value="formData.house_no_street" placeholder="House No./Blk/Street" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Purok <span v-if="mode === 'add'" class="text-red-500">*</span>
              </label>
              <NSelect
                v-model:value="formData.purok_id"
                :options="purokOptions"
                placeholder="Select Purok"
              />
            </div>
          </div>

          <!-- RFID Information -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                RFID No. <span v-if="mode === 'add'" class="text-red-500">*</span>
              </label>
              <NInput v-model:value="formData.rfid_uid" placeholder="RFID Number" />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1.5">RFID Status</label>
              <div class="flex items-center gap-2 mt-2">
                <NSwitch v-model:value="formData.is_active" />
                <span class="text-sm text-gray-700">
                  {{ formData.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="mode === 'view'">
            <NCollapse>
              <NCollapseItem title="Transaction History" name="transactions">
                <NSpin v-if="transactionLoading" size="small" class="py-4" />
                <NDataTable
                  v-else
                  :columns="transactionColumns"
                  :data="transactionHistory"
                  :bordered="false"
                  size="small"
                  :empty-text="'No transaction history found'"
                />
              </NCollapseItem>
            </NCollapse>
          </div>
        </div>
      </div>

      <!-- FOOTER -->
      <div class="flex justify-end gap-3 px-6 py-4 border-t">
        <NButton @click="handleClose" :disabled="saving">
          Cancel
        </NButton>

        <NButton
          type="primary"
          @click="handleSave"
          :loading="saving"
          :disabled="saving || (mode === 'view' && !isFormChanged)"
        >
          Save
        </NButton>
      </div>
    </div>
  </NModal>
</template>