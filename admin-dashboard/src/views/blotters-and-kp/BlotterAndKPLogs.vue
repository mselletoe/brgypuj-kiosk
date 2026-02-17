<script setup>
import { ref, computed, h, watch, onMounted } from 'vue'
import {
  NDataTable,
  NInput,
  NButton,
  NCheckbox,
  NModal,
  NSelect,
  NDatePicker,
  useMessage
} from 'naive-ui'
import { FunnelIcon, TrashIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getAllBlotters,
  createBlotter,
  updateBlotter,
  deleteBlotter,
  bulkDeleteBlotters
} from '@/api/blotterService'
import { fetchResidents } from '@/api/residentService'

const message = useMessage()

// ======================================
// State Management
// ======================================
const blotters = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedIds = ref([])
const showDeleteModal = ref(false)
const showBlotterModal = ref(false)
const currentBlotter = ref(null)
const modalMode = ref('add')
const saving = ref(false)
const formData = ref({})

// Residents for the selector dropdowns
const residents = ref([])

// ======================================
// Data Loading
// ======================================
async function loadBlotters() {
  loading.value = true
  try {
    const data = await getAllBlotters()
    blotters.value = data.map(normalizeRecord)
  } catch {
    message.error('Failed to load blotter records')
  } finally {
    loading.value = false
  }
}

async function loadResidents() {
  try {
    const data = await fetchResidents()
    residents.value = data
  } catch {
    message.error('Failed to load residents')
  }
}

onMounted(() => {
  loadBlotters()
  loadResidents()
})

// ======================================
// Resident Selector Options
// ======================================
const residentOptions = computed(() =>
  residents.value.map(r => ({
    label: r.full_name || [r.first_name, r.middle_name, r.last_name].filter(Boolean).join(' ') || `Resident #${r.id}`,
    value: r.id,
    resident: r
  }))
)

function handleComplainantSelect(residentId) {
  if (!residentId) {
    // Cleared — reset complainant fields
    formData.value.complainant_id = null
    formData.value.complainant_name = ''
    formData.value.complainant_age = null
    formData.value.complainant_address = ''
    return
  }
  const option = residentOptions.value.find(o => o.value === residentId)
  if (!option) return
  const r = option.resident
  formData.value.complainant_id = r.id
  formData.value.complainant_name = option.label
  formData.value.complainant_age = r.age ?? null
  formData.value.complainant_address = r.address ?? ''
}

function handleRespondentSelect(residentId) {
  if (!residentId) {
    formData.value.respondent_id = null
    formData.value.respondent_name = ''
    formData.value.respondent_age = null
    formData.value.respondent_address = ''
    return
  }
  const option = residentOptions.value.find(o => o.value === residentId)
  if (!option) return
  const r = option.resident
  formData.value.respondent_id = r.id
  formData.value.respondent_name = option.label
  formData.value.respondent_age = r.age ?? null
  formData.value.respondent_address = r.address ?? ''
}

// ======================================
// Data Normalization
// ======================================
function normalizeRecord(record) {
  return {
    ...record,
    date: record.incident_date ? new Date(record.incident_date).getTime() : null,
    time: record.incident_time ? record.incident_time.slice(0, 5) : ''
  }
}

function toApiPayload(form) {
  const payload = { ...form }

  if (form.date) {
    payload.incident_date = new Date(form.date).toISOString().split('T')[0]
  } else {
    payload.incident_date = null
  }

  payload.incident_time = form.time || null

  // Remove frontend-only fields
  const remove = [
    'date', 'time', 'id', 'blotter_no', 'created_at',
    'complainant_resident_name', 'complainant_resident_first_name',
    'complainant_resident_middle_name', 'complainant_resident_last_name',
    'complainant_resident_phone',
    'respondent_resident_name', 'respondent_resident_first_name',
    'respondent_resident_middle_name', 'respondent_resident_last_name',
    'respondent_resident_phone',
  ]
  remove.forEach(k => delete payload[k])

  return payload
}

// ======================================
// Selection Logic
// ======================================
const filteredBlotters = computed(() => {
  if (!searchQuery.value) return blotters.value
  const query = searchQuery.value.toLowerCase()
  return blotters.value.filter(b =>
    b.blotter_no.toLowerCase().includes(query) ||
    b.complainant_name.toLowerCase().includes(query) ||
    (b.incident_type && b.incident_type.toLowerCase().includes(query))
  )
})

const totalCount = computed(() => filteredBlotters.value.length)
const selectedCount = computed(() => selectedIds.value.length)

const selectionState = computed(() => {
  if (totalCount.value === 0 || selectedCount.value === 0) return 'none'
  if (selectedCount.value < totalCount.value) return 'partial'
  return 'all'
})

function handleMainSelectToggle() {
  if (selectionState.value === 'all' || selectionState.value === 'partial') {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredBlotters.value.map(b => b.id)
  }
}

watch(searchQuery, () => { selectedIds.value = [] })

// ======================================
// Format Helpers
// ======================================
function formatDate(timestamp) {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleDateString('en-PH', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

// ======================================
// CRUD Operations
// ======================================
function openAddModal() {
  modalMode.value = 'add'
  currentBlotter.value = null
  showBlotterModal.value = true
}

function openViewModal(blotter) {
  modalMode.value = 'view'
  currentBlotter.value = { ...blotter }
  showBlotterModal.value = true
}

function handleModalClose() {
  showBlotterModal.value = false
  currentBlotter.value = null
}

// ======================================
// Delete Operations
// ======================================
function requestBulkDelete() {
  if (selectedIds.value.length === 0) {
    message.warning('Please select records to delete')
    return
  }
  showDeleteModal.value = true
}

async function confirmDelete() {
  try {
    await bulkDeleteBlotters(selectedIds.value)
    blotters.value = blotters.value.filter(b => !selectedIds.value.includes(b.id))
    message.success(`${selectedIds.value.length} record(s) deleted successfully`)
    selectedIds.value = []
    showDeleteModal.value = false
  } catch {
    message.error('Failed to delete some records')
  }
}

async function handleDeleteSingle(id) {
  try {
    await deleteBlotter(id)
    blotters.value = blotters.value.filter(b => b.id !== id)
    message.success('Blotter record deleted successfully')
  } catch {
    message.error('Failed to delete record')
  }
}

// ======================================
// Table Columns
// ======================================
const columns = computed(() => [
  {
    title: '',
    key: 'select',
    width: 50,
    render(row) {
      return h(NCheckbox, {
        checked: selectedIds.value.includes(row.id),
        onUpdateChecked(checked) {
          if (checked) {
            if (!selectedIds.value.includes(row.id)) selectedIds.value.push(row.id)
          } else {
            selectedIds.value = selectedIds.value.filter(id => id !== row.id)
          }
        }
      })
    }
  },
  {
    title: 'Blotter No.',
    key: 'blotter_no',
    width: 130,
    render(row) {
      return h('span', { class: 'font-bold text-blue-700' }, row.blotter_no)
    }
  },
  {
    title: 'Complainant',
    key: 'complainant_name',
    minWidth: 160
  },
  {
    title: 'Respondent',
    key: 'respondent_name',
    minWidth: 160,
    render(row) { return row.respondent_name || 'N/A' }
  },
  {
    title: 'Date',
    key: 'date',
    width: 140,
    render(row) { return formatDate(row.date) }
  },
  {
    title: 'Type of Incident',
    key: 'incident_type',
    minWidth: 180,
    render(row) { return row.incident_type || 'N/A' }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 130,
    render(row) {
      return h('div', { class: 'flex gap-2 items-center' }, [
        h(NButton, { type: 'info', size: 'small', onClick: () => openViewModal(row) }, { default: () => 'View' }),
        h('button', { onClick: () => handleDeleteSingle(row.id), class: 'p-1.5 text-red-500 hover:bg-red-50 rounded transition' }, [h(TrashIcon, { class: 'w-5 h-5' })])
      ])
    }
  }
])

// ======================================
// Modal Form State
// ======================================
const incidentTypeOptions = [
  { label: 'Physical Altercation (Pananakit o Pisikal na Pag-aaway)', value: 'Physical Altercation' },
  { label: 'Verbal Dispute (Pagmumura o Pag-aaway sa Salita)', value: 'Verbal Dispute' },
  { label: 'Property Dispute (Away sa Lupa o Hangganan)', value: 'Property Dispute' },
  { label: 'Unpaid Debt (Utang na Hindi Nababayaran)', value: 'Unpaid Debt' },
  { label: 'Noise Complaint (Reklamo sa Ingay (Videoke, atbp.))', value: 'Noise Complaint' },
  { label: 'Theft (Pagnanakaw)', value: 'Theft' },
  { label: 'Trespassing (Pagpasok nang Walang Pahintulot)', value: 'Trespassing' },
  { label: 'Domestic Disturbance (Gulo sa Loob ng Tahanan)', value: 'Domestic Disturbance' },
  { label: 'Lost Item/Document (Nawawalang Gamit o Dokumento)', value: 'Lost Item/Document' },
  { label: 'Vehicular Accident (Aksidente sa Sasakyan)', value: 'Vehicular Accident' },
  { label: 'Stray Animal/Pet Issue (Reklamo sa Pagala-galang Hayop)', value: 'Stray Animal/Pet Issue' },
  { label: 'Vandalism (Paninira ng Ari-arian / Graffitti)', value: 'Vandalism' },
  { label: 'Threats (Pananakot)', value: 'Threats' },
  { label: 'Slander/Libel (Paninirang-puri)', value: 'Slander' },
  { label: 'Other', value: 'Other' }
]

function emptyForm() {
  return {
    complainant_id: null,
    complainant_name: '',
    complainant_age: null,
    complainant_address: '',
    respondent_id: null,
    respondent_name: '',
    respondent_age: null,
    respondent_address: '',
    date: new Date().getTime(),
    time: '',
    incident_place: '',
    incident_type: null,
    narrative: '',
    recorded_by: '',
    contact_no: ''
  }
}

watch(() => showBlotterModal.value, (val) => {
  if (val) {
    formData.value = modalMode.value === 'view' && currentBlotter.value
      ? { ...currentBlotter.value }
      : emptyForm()
  }
})

async function handleSave() {
  if (!formData.value.complainant_name) {
    message.error('Complainant name is required')
    return
  }

  saving.value = true
  try {
    const payload = toApiPayload(formData.value)

    if (modalMode.value === 'add') {
      const created = await createBlotter(payload)
      blotters.value.unshift(normalizeRecord(created))
      message.success('Blotter record added successfully')
    } else {
      const updated = await updateBlotter(currentBlotter.value.id, payload)
      const idx = blotters.value.findIndex(b => b.id === currentBlotter.value.id)
      if (idx !== -1) blotters.value[idx] = normalizeRecord(updated)
      message.success('Blotter record updated successfully')
    }

    showBlotterModal.value = false
  } catch {
    message.error(modalMode.value === 'add' ? 'Failed to add blotter record' : 'Failed to update blotter record')
  } finally {
    saving.value = false
  }
}

const modalTitle = computed(() => {
  if (modalMode.value === 'add') return 'Add New Blotter Record'
  return formData.value.blotter_no ? `Blotter # ${formData.value.blotter_no}` : 'Blotter Record'
})
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Blotter and KP Logs" />
        <p class="text-sm text-gray-500 mt-1">Manage Blotter and KP logs for residents</p>
      </div>

      <div class="flex items-center gap-3">
        <n-input v-model:value="searchQuery" placeholder="Search" style="width: 250px" clearable />

        <button class="p-2 border border-gray-400 rounded-lg hover:bg-gray-50 transition-colors">
          <FunnelIcon class="w-5 h-5 text-gray-700" />
        </button>

        <button
          @click="requestBulkDelete"
          :disabled="selectionState === 'none'"
          class="p-2 border border-red-400 rounded-lg transition-colors"
          :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'"
        >
          <TrashIcon class="w-5 h-5 text-red-500" />
        </button>

        <div
          class="flex items-center border rounded-lg overflow-hidden transition-colors"
          :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
        >
          <button @click="handleMainSelectToggle" class="p-2 hover:bg-gray-50 flex items-center">
            <div
              class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
              :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'"
            >
              <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
              <CheckIcon v-if="selectionState === 'all'" class="w-3 h-3 text-white" />
            </div>
          </button>
        </div>

        <button
          @click="openAddModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200">
      <n-data-table :columns="columns" :data="filteredBlotters" :loading="loading" :bordered="false" />
    </div>

    <!-- ================================ -->
    <!-- Blotter Modal -->
    <!-- ================================ -->
    <NModal :show="showBlotterModal" @update:show="handleModalClose" :mask-closable="false">
      <div class="w-[820px] max-h-[90vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col" role="dialog" aria-modal="true">

        <!-- Modal Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
          <h2 class="text-lg font-semibold text-gray-800">{{ modalTitle }}</h2>
          <button @click="handleModalClose" class="p-1 rounded hover:bg-gray-200 transition">
            <XMarkIcon class="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <!-- Modal Body -->
        <div class="px-6 py-5 overflow-y-auto space-y-5">

          <!-- Blotter Header Info -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Blotter No.</label>
              <n-input
                :value="modalMode === 'view' ? formData.blotter_no : 'Auto-generated'"
                :disabled="true"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Date</label>
              <NDatePicker v-model:value="formData.date" type="date" placeholder="Select Date" class="w-full" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Time</label>
              <n-input v-model:value="formData.time" placeholder="e.g. 14:30" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Place of Incident</label>
            <n-input v-model:value="formData.incident_place" placeholder="Location of the incident" />
          </div>

          <!-- ======================== -->
          <!-- Complainant Section -->
          <!-- ======================== -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Complainant (Nagreklamo)</p>

            <!-- Resident Selector -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Registered Resident
                <span class="text-gray-400 font-normal">(optional — select to auto-fill)</span>
              </label>
              <NSelect
                v-model:value="formData.complainant_id"
                :options="residentOptions"
                filterable
                clearable
                placeholder="Search resident by name..."
                @update:value="handleComplainantSelect"
              />
            </div>

            <!-- Manual Fields (auto-filled if resident selected, editable otherwise) -->
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  Full Name <span class="text-red-500">*</span>
                </label>
                <n-input
                  v-model:value="formData.complainant_name"
                  placeholder="Full Name"
                  :disabled="!!formData.complainant_id"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input
                  v-model:value="formData.complainant_age"
                  placeholder="Age"
                  type="number"
                  :disabled="!!formData.complainant_id"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input
                  v-model:value="formData.complainant_address"
                  placeholder="Address"
                  :disabled="!!formData.complainant_id"
                />
              </div>
            </div>
          </div>

          <!-- ======================== -->
          <!-- Respondent Section -->
          <!-- ======================== -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Respondent (Inireklamo)</p>

            <!-- Resident Selector -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Registered Resident
                <span class="text-gray-400 font-normal">(optional — select to auto-fill)</span>
              </label>
              <NSelect
                v-model:value="formData.respondent_id"
                :options="residentOptions"
                filterable
                clearable
                placeholder="Search resident by name..."
                @update:value="handleRespondentSelect"
              />
            </div>

            <!-- Manual Fields -->
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                <n-input
                  v-model:value="formData.respondent_name"
                  placeholder="Full Name"
                  :disabled="!!formData.respondent_id"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input
                  v-model:value="formData.respondent_age"
                  placeholder="Age"
                  type="number"
                  :disabled="!!formData.respondent_id"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input
                  v-model:value="formData.respondent_address"
                  placeholder="Address"
                  :disabled="!!formData.respondent_id"
                />
              </div>
            </div>
          </div>

          <!-- Incident Details -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Incident Details</p>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Type of Incident</label>
              <NSelect v-model:value="formData.incident_type" :options="incidentTypeOptions" placeholder="Select Type" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Narrative of Events</label>
              <n-input v-model:value="formData.narrative" type="textarea" placeholder="Describe what happened..." :rows="4" />
            </div>
          </div>

          <!-- Record Information -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Record Information</p>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Recorded By</label>
                <n-input v-model:value="formData.recorded_by" placeholder="Name of officer" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Contact No.</label>
                <n-input v-model:value="formData.contact_no" placeholder="09XXXXXXXXX" />
              </div>
            </div>
          </div>

        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end gap-3 px-6 py-4 border-t">
          <NButton @click="handleModalClose" :disabled="saving">Cancel</NButton>
          <NButton type="primary" @click="handleSave" :loading="saving" :disabled="saving">Save</NButton>
        </div>
      </div>
    </NModal>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :show="showDeleteModal"
      :title="`Delete ${selectedIds.length} record(s)?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>