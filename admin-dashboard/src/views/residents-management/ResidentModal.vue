<script setup>
import { ref, watch, computed, onMounted, h } from 'vue'
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
import { fetchResidentBlotterRecords } from '@/api/blotterService'

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
  barangay: 'Poblacion I',
  municipality: 'Amadeo',
  province: 'Cavite',
  region: 'Region IV-A',
  
  // RFID Info
  rfid_uid: '',
  is_active: true
})

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
    message.error('Failed to load transaction history')
  } finally {
    transactionLoading.value = false
  }
}

function parseDateToTimestamp(str) {
  if (!str) return null
  // Handle "MM/DD/YYYY" format from backend
  const [month, day, year] = str.split('/')
  if (month && day && year) {
    return new Date(Number(year), Number(month) - 1, Number(day)).getTime()
  }
  // Fallback for ISO "YYYY-MM-DD" format
  return new Date(str).getTime()
}

// Blotter records (only loaded in view mode)
const blotterRecords = ref([])
const blotterLoading = ref(false)

const blotterColumns = [
  {
    title: 'Blotter No.',
    key: 'blotter_no',
    width: 130,
    render(row) {
      return h('span', { class: 'font-bold text-blue-700' }, row.blotter_no)
    }
  },
  {
    title: 'Role',
    key: 'role',
    width: 115,
    render(row) {
      return row.role || '—'
    }
  },
  {
    title: 'Incident Type',
    key: 'incident_type',
    render(row) {
      return row.incident_type || '—'
    }
  },
  {
    title: 'Incident Date',
    key: 'incident_date',
    width: 130,
    render(row) {
      // Handle both raw API string (incident_date) and normalized timestamp (date)
      const raw = row.incident_date || (row.date ? new Date(row.date).toISOString().split('T')[0] : null)
      if (!raw) return '—'
      return new Date(raw).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    }
  },
  {
    title: 'Incident Place',
    key: 'incident_place',
    render(row) {
      return row.incident_place || '—'
    }
  },
  {
    title: 'Filed On',
    key: 'created_at',
    width: 130,
    render(row) {
      if (!row.created_at) return '—'
      return new Date(row.created_at).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    }
  }
]

async function loadBlotterRecords() {
  blotterLoading.value = true
  try {
    blotterRecords.value = await fetchResidentBlotterRecords(props.residentId)
  } catch (error) {
    message.error('Failed to load blotter records')
  } finally {
    blotterLoading.value = false
  }
}

// Photo preview computed from base64 bytes (backend returns bytes)
const photoUrl = computed(() => {
  if (!residentDetails.value?.photo) return null
  // photo comes as a base64 string from the API
  const photo = residentDetails.value.photo
  if (typeof photo === 'string') {
    return photo.startsWith('data:') ? photo : `data:image/jpeg;base64,${photo}`
  }
  return null
})

// Brgy ID expiration — formatted for display, with status tag
const brgyIdExpiration = computed(() => {
  const raw = residentDetails.value?.brgy_id_expiration_date
  if (!raw) return null
  const d = new Date(raw + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const msLeft = d - today
  const daysLeft = Math.ceil(msLeft / (1000 * 60 * 60 * 24))
  const formatted = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  if (daysLeft < 0)   return { text: formatted, label: 'Expired',           color: 'text-red-600 bg-red-50 border-red-200' }
  if (daysLeft <= 30) return { text: formatted, label: `${daysLeft}d left`,  color: 'text-amber-600 bg-amber-50 border-amber-200' }
  return               { text: formatted, label: 'Active',            color: 'text-green-600 bg-green-50 border-green-200' }
})

// Human-readable residency duration label
const residencyLabel = computed(() => {
  return residentDetails.value?.residency_label || 
    `${residentDetails.value?.years_of_residency ?? 0} year(s)`
})

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
    message.error('Failed to load puroks')
  }
})

// Load resident details when modal opens in view mode
watch(() => props.show, async (newVal) => {
  if (newVal) {
    if (props.mode === 'view' && props.residentId) {
      // Load resident details, transaction history, and blotter records
      await loadResidentDetails()
      await loadTransactionHistory()
      await loadBlotterRecords()
    } else if (props.mode === 'add') {
      // Reset all data for clean state
      transactionHistory.value = []
      blotterRecords.value = []
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
      birthdate: parseDateToTimestamp(data.birthdate),
      residency_start_date: parseDateToTimestamp(data.residency_start_date),
      phone_number: data.phone_number || '',
      email: data.email || '',
      house_no_street: data.current_address?.house_no_street || '',
      purok_id: data.current_address?.purok_id || null,
      barangay: data.current_address?.barangay || 'Poblacion I',
      municipality: data.current_address?.municipality || 'Amadeo',
      province: data.current_address?.province || 'Cavite',
      region: data.current_address?.region || 'Region IV-A',
      rfid_uid: data.active_rfid?.rfid_uid || '',
      is_active: data.active_rfid?.is_active ?? true
    }

    originalFormData.value = JSON.parse(JSON.stringify(formData.value))

  } catch (error) {
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
    barangay: 'Poblacion I',
    municipality: 'Amadeo',
    province: 'Cavite',
    region: 'Region IV-A',
    rfid_uid: '',
    is_active: true
  }

  originalFormData.value = JSON.parse(JSON.stringify(formData.value))
}

function formatDateForAPI(timestamp) {
  if (!timestamp) return null
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function handleSave() {
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
  }
  
  saving.value = true
  
  try {
    if (props.mode === 'add') {
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
        }
      }
      
      await createResident(payload)
      message.success('Resident registered successfully')
    } else {
      const updatePayload = {
        first_name: formData.value.first_name,
        middle_name: formData.value.middle_name || null,
        last_name: formData.value.last_name,
        suffix: formData.value.suffix || null,
        gender: formData.value.gender,
        birthdate: formatDateForAPI(formData.value.birthdate),
        residency_start_date: formatDateForAPI(formData.value.residency_start_date),
        email: formData.value.email || null,
        phone_number: formData.value.phone_number || null
      }


      await updateResident(props.residentId, updatePayload)
      
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
      
      if (formData.value.rfid_uid) {
        await updateResidentRFID(props.residentId, {
          is_active: formData.value.is_active
        })
      }
      
      message.success('Resident updated successfully')
    }
    
    emit('saved')
  } catch (error) {
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
      <div v-else class="px-8 py-6 space-y-6 overflow-y-auto">

        <!-- VIEW MODE: Resident Summary Banner (photo + key stats) -->
        <div v-if="mode === 'view' && residentDetails" class="flex items-center gap-8 p-4 bg-gray-50 rounded-xl border border-gray-200">
          <!-- Photo -->
          <div class="flex-shrink-0">
            <img
              v-if="photoUrl"
              :src="photoUrl"
              alt="Resident photo"
              class="w-20 h-20 rounded-full object-cover border-2 border-gray-300 shadow-sm"
            />
            <div
              v-else
              class="w-20 h-20 rounded-full bg-gray-200 border-2 border-gray-300 flex items-center justify-center shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
          <!-- Stats -->
          <div class="flex gap-6 justify-between">
            <!-- Age -->
            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Age</span>
              <span class="text-2xl font-bold text-gray-800">{{ residentDetails.age }}</span>
              <span class="text-xs text-gray-400">years old</span>
            </div>

            <div class="w-[1.1px] bg-gray-300 self-stretch"></div>

            <!-- Residency -->
            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Residency</span>
              <span class="text-2xl font-bold text-gray-800">{{ residencyLabel }}</span>
              <span class="text-xs text-gray-400">since {{ residentDetails.residency_start_date }}</span>
            </div>

            <div class="w-[1.1px] bg-gray-300 self-stretch"></div>

            <!-- Brgy. ID Number -->
            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Brgy. I.D No.</span>
              <span class="text-2xl font-bold text-gray-800">{{ residentDetails.brgy_id_number || '—' }}</span>
              <template v-if="brgyIdExpiration">
                <span class="text-xs text-gray-400">Expires {{ brgyIdExpiration.text }}</span>
                <span :class="['text-[10px] font-semibold px-2 py-0.5 rounded-full border w-fit', brgyIdExpiration.color]">
                  {{ brgyIdExpiration.label }}
                </span>
              </template>
              <span v-else class="text-xs text-gray-400 italic">No expiry on record</span>
            </div>

            <div class="w-[1.1px] bg-gray-300 self-stretch"></div>
            
            <!-- RFID Number -->
            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">RFID No.</span>
              <span class="text-2xl font-bold text-blue-700">{{ formData.rfid_uid || '—' }}</span>
              <div class="flex items-center gap-2">
                <NSwitch
                  v-model:value="formData.is_active"
                  :disabled="!formData.rfid_uid"
                  size="small"
                />
                <span class="text-xs" :class="formData.rfid_uid ? 'text-gray-700' : 'text-gray-400'">
                  {{ !formData.rfid_uid ? 'No RFID' : formData.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <!-- ADD/EDIT MODE - Form -->
        <div class="flex flex-col gap-4">
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
          <div class="grid grid-cols-3 gap-4 mb-3">
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
          <div class="flex flex-col gap-2">
            <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Contact Information</span>
            <div class="grid grid-cols-2 gap-4 mb-3">
              <div>
                <label class="block text-sm text-gray-700 mb-1.5">Phone Number</label>
                <NInput v-model:value="formData.phone_number" placeholder="09123456789" />
              </div>
              <div>
                <label class="block text-sm text-gray-700 mb-1.5">Email</label>
                <NInput v-model:value="formData.email" type="email" placeholder="email@example.com" />
              </div>
            </div>            
          </div>

          <!-- Address -->
          <div class="flex flex-col gap-2 mb-3">
            <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Address</span>

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
          </div>

          <hr class="bg-slate-300 my-5" />

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

              <NCollapseItem title="Blotter Records" name="blotter">
                <NSpin v-if="blotterLoading" size="small" class="py-4" />
                <NDataTable
                  v-else
                  :columns="blotterColumns"
                  :data="blotterRecords"
                  :bordered="false"
                  size="small"
                  :empty-text="'No blotter records found'"
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