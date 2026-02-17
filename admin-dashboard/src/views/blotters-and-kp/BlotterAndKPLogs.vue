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
  NTimePicker,
  NSpin,
  NCollapse,
  NCollapseItem,
  useMessage
} from 'naive-ui'
import { FunnelIcon, TrashIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

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

// ======================================
// Mock Data
// ======================================
const mockBlotters = [
  {
    id: 1,
    blotter_no: '2026-0001',
    complainant_name: 'Juan dela Cruz',
    complainant_age: 34,
    complainant_address: 'Purok 2, Poblacion Uno, Amadeo, Cavite',
    respondent_name: 'Pedro Santos',
    respondent_age: 40,
    respondent_address: 'Purok 3, Poblacion Uno, Amadeo, Cavite',
    date: new Date('2026-01-15').getTime(),
    time: '14:30',
    place: 'Barangay Hall vicinity',
    incident_type: 'Physical Altercation',
    narrative: 'The complainant reported that the respondent punched him without provocation while he was walking near the barangay hall.',
    recorded_by: 'Brgy. Tanod Jose Reyes',
    contact_no: '09171234567'
  },
  {
    id: 2,
    blotter_no: '2026-0002',
    complainant_name: 'Maria Santos',
    complainant_age: 28,
    complainant_address: 'Purok 1, Poblacion Uno, Amadeo, Cavite',
    respondent_name: 'Ana Gomez',
    respondent_age: 32,
    respondent_address: 'Purok 1, Poblacion Uno, Amadeo, Cavite',
    date: new Date('2026-01-22').getTime(),
    time: '09:15',
    place: 'Market area',
    incident_type: 'Verbal Dispute',
    narrative: 'The complainant reported verbal harassment and threats from the respondent at the local market.',
    recorded_by: 'Brgy. Secretary Lorna Diaz',
    contact_no: '09189876543'
  },
  {
    id: 3,
    blotter_no: '2026-0003',
    complainant_name: 'Roberto Villanueva',
    complainant_age: 55,
    complainant_address: 'Purok 4, Poblacion Uno, Amadeo, Cavite',
    respondent_name: 'Carlos Mendoza',
    respondent_age: 30,
    respondent_address: 'Purok 2, Poblacion Uno, Amadeo, Cavite',
    date: new Date('2026-02-03').getTime(),
    time: '18:00',
    place: 'Respondent\'s property boundary',
    incident_type: 'Property Dispute',
    narrative: 'The complainant alleges that the respondent encroached on his property by building a fence beyond the agreed boundary.',
    recorded_by: 'Brgy. Tanod Jose Reyes',
    contact_no: '09171234567'
  }
]

// ======================================
// Data Loading
// ======================================
async function loadBlotters() {
  loading.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    blotters.value = mockBlotters
  } catch (error) {
    console.error('Failed to load blotter records:', error)
    message.error('Failed to load blotter records')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBlotters()
})

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

watch(searchQuery, () => {
  selectedIds.value = []
})

// ======================================
// Format Date
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
    blotters.value = blotters.value.filter(b => !selectedIds.value.includes(b.id))
    message.success(`${selectedIds.value.length} record(s) deleted successfully`)
    selectedIds.value = []
    showDeleteModal.value = false
  } catch (error) {
    console.error('Failed to delete records:', error)
    message.error('Failed to delete some records')
  }
}

async function handleDeleteSingle(id) {
  try {
    blotters.value = blotters.value.filter(b => b.id !== id)
    message.success('Blotter record deleted successfully')
  } catch (error) {
    console.error('Failed to delete record:', error)
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
    title: 'Date',
    key: 'date',
    width: 140,
    render(row) {
      return formatDate(row.date)
    }
  },
  {
    title: 'Type of Incident',
    key: 'incident_type',
    minWidth: 180,
    render(row) {
      return row.incident_type || 'N/A'
    }
  },
  {
    title: 'Contact No.',
    key: 'contact_no',
    width: 150,
    render(row) {
      return row.contact_no || 'N/A'
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 130,
    render(row) {
      return h('div', { class: 'flex gap-2 items-center' }, [
        h(
          NButton,
          {
            type: 'info',
            size: 'small',
            onClick: () => openViewModal(row)
          },
          { default: () => 'View' }
        ),
        h(
          'button',
          {
            onClick: () => handleDeleteSingle(row.id),
            class: 'p-1.5 text-red-500 hover:bg-red-50 rounded transition'
          },
          [h(TrashIcon, { class: 'w-5 h-5' })]
        )
      ])
    }
  }
])

// ======================================
// Modal Form State
// ======================================
const saving = ref(false)
const formData = ref({})

const incidentTypeOptions = [
  { label: 'Physical Altercation', value: 'Physical Altercation' },
  { label: 'Verbal Dispute', value: 'Verbal Dispute' },
  { label: 'Property Dispute', value: 'Property Dispute' },
  { label: 'Noise Complaint', value: 'Noise Complaint' },
  { label: 'Theft', value: 'Theft' },
  { label: 'Trespassing', value: 'Trespassing' },
  { label: 'Domestic Disturbance', value: 'Domestic Disturbance' },
  { label: 'Other', value: 'Other' }
]

watch(() => showBlotterModal.value, (val) => {
  if (val) {
    if (modalMode.value === 'view' && currentBlotter.value) {
      formData.value = { ...currentBlotter.value }
    } else {
      formData.value = {
        blotter_no: '',
        complainant_name: '',
        complainant_age: null,
        complainant_address: '',
        respondent_name: '',
        respondent_age: null,
        respondent_address: '',
        date: new Date().getTime(),
        time: '',
        place: '',
        incident_type: null,
        narrative: '',
        recorded_by: '',
        contact_no: ''
      }
    }
  }
})

function handleSave() {
  if (!formData.value.complainant_name) {
    message.error('Complainant name is required')
    return
  }
  saving.value = true
  setTimeout(() => {
    if (modalMode.value === 'add') {
      const newRecord = {
        ...formData.value,
        id: Date.now(),
        blotter_no: formData.value.blotter_no || `2026-${String(blotters.value.length + 1).padStart(4, '0')}`
      }
      blotters.value.unshift(newRecord)
      message.success('Blotter record added successfully')
    } else {
      const idx = blotters.value.findIndex(b => b.id === formData.value.id)
      if (idx !== -1) blotters.value[idx] = { ...formData.value }
      message.success('Blotter record updated successfully')
    }
    saving.value = false
    showBlotterModal.value = false
  }, 600)
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

      <!-- Action Buttons -->
      <div class="flex items-center gap-3">
        <!-- Search -->
        <n-input
          v-model:value="searchQuery"
          placeholder="Search"
          style="width: 250px"
          clearable
        />

        <!-- Filter Button -->
        <button
          class="p-2 border border-gray-400 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <FunnelIcon class="w-5 h-5 text-gray-700" />
        </button>

        <!-- Bulk Delete Button -->
        <button
          @click="requestBulkDelete"
          :disabled="selectionState === 'none'"
          class="p-2 border border-red-400 rounded-lg transition-colors"
          :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'"
        >
          <TrashIcon class="w-5 h-5 text-red-500" />
        </button>

        <!-- Select All Toggle -->
        <div
          class="flex items-center border rounded-lg overflow-hidden transition-colors"
          :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
        >
          <button
            @click="handleMainSelectToggle"
            class="p-2 hover:bg-gray-50 flex items-center"
          >
            <div
              class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
              :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'"
            >
              <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
              <CheckIcon v-if="selectionState === 'all'" class="w-3 h-3 text-white" />
            </div>
          </button>
        </div>

        <!-- Add Blotter Button -->
        <button
          @click="openAddModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Blotter
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200">
      <n-data-table
        :columns="columns"
        :data="filteredBlotters"
        :loading="loading"
        :bordered="false"
      />
    </div>

    <!-- ================================ -->
    <!-- Blotter Modal -->
    <!-- ================================ -->
    <NModal
      :show="showBlotterModal"
      @update:show="handleModalClose"
      :mask-closable="false"
    >
      <div
        class="w-[820px] max-h-[90vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col"
        role="dialog"
        aria-modal="true"
      >
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
              <n-input v-model:value="formData.blotter_no" placeholder="e.g. 2026-0001" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Date</label>
              <NDatePicker
                v-model:value="formData.date"
                type="date"
                placeholder="Select Date"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Time</label>
              <n-input v-model:value="formData.time" placeholder="e.g. 14:30" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Place of Incident</label>
            <n-input v-model:value="formData.place" placeholder="Location of the incident" />
          </div>

          <!-- Divider -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Complainant (Nagreklamo)</p>
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-1">
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  Full Name <span class="text-red-500">*</span>
                </label>
                <n-input v-model:value="formData.complainant_name" placeholder="Full Name" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input
                  v-model:value="formData.complainant_age"
                  placeholder="Age"
                  type="number"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input v-model:value="formData.complainant_address" placeholder="Address" />
              </div>
            </div>
          </div>

          <!-- Respondent -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Respondent (Inireklamo)</p>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                <n-input v-model:value="formData.respondent_name" placeholder="Full Name" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input
                  v-model:value="formData.respondent_age"
                  placeholder="Age"
                  type="number"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input v-model:value="formData.respondent_address" placeholder="Address" />
              </div>
            </div>
          </div>

          <!-- Incident Details -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Incident Details</p>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Type of Incident</label>
              <NSelect
                v-model:value="formData.incident_type"
                :options="incidentTypeOptions"
                placeholder="Select Type"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Narrative of Events
              </label>
              <n-input
                v-model:value="formData.narrative"
                type="textarea"
                placeholder="Describe what happened..."
                :rows="4"
              />
            </div>
          </div>

          <!-- Recorded By -->
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
          <NButton
            type="primary"
            @click="handleSave"
            :loading="saving"
            :disabled="saving"
          >
            Save
          </NButton>
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