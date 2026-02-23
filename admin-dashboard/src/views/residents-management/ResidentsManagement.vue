<script setup>
import { ref, computed, h, watch, onMounted } from 'vue'
import { NDataTable, NInput, NButton, NCheckbox, useMessage } from 'naive-ui'
import { FunnelIcon, TrashIcon, CheckIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentModal from './ResidentModal.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import { 
  fetchResidents, 
  deleteResident as deleteResidentAPI 
} from '@/api/residentService'

const message = useMessage()

// ======================================
// State Management
// ======================================
const residents = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedIds = ref([])
const showDeleteModal = ref(false)
const showFilterModal = ref(false)
const showResidentModal = ref(false)
const currentResident = ref(null)
const modalMode = ref('add')
const showSingleDeleteModal = ref(false)
const pendingDeleteId = ref(null)

// ======================================
// Data Loading
// ======================================
async function loadResidents() {
  loading.value = true
  try {
    const data = await fetchResidents()
    residents.value = data
  } catch (error) {
    console.error('Failed to load residents:', error)
    message.error('Failed to load residents')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadResidents()
})

// ======================================
// Selection Logic
// ======================================
const filteredResidents = computed(() => {
  if (!searchQuery.value) return residents.value
  
  const query = searchQuery.value.toLowerCase()
  return residents.value.filter(r => 
    r.full_name.toLowerCase().includes(query) ||
    (r.phone_number && r.phone_number.includes(query)) ||
    (r.rfid_no && r.rfid_no.toLowerCase().includes(query)) ||
    (r.current_address && r.current_address.toLowerCase().includes(query))
  )
})

const totalCount = computed(() => filteredResidents.value.length)
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
    selectedIds.value = filteredResidents.value.map(r => r.id)
  }
}

// Clear selections when search changes
watch(searchQuery, () => {
  selectedIds.value = []
})

// ======================================
// CRUD Operations
// ======================================
function openAddModal() {
  modalMode.value = 'add'
  currentResident.value = null
  showResidentModal.value = true
}

function openViewModal(resident) {
  modalMode.value = 'view'
  currentResident.value = resident
  showResidentModal.value = true
}

function handleModalClose() {
  showResidentModal.value = false
  currentResident.value = null
}

function handleResidentSaved() {
  showResidentModal.value = false
  currentResident.value = null
  loadResidents() // Reload the table
}

// ======================================
// Delete Operations
// ======================================
function requestBulkDelete() {
  if (selectedIds.value.length === 0) {
    message.warning('Please select residents to delete')
    return
  }
  showDeleteModal.value = true
}

async function confirmDelete() {
  try {
    // Delete all selected residents
    await Promise.all(
      selectedIds.value.map(id => deleteResidentAPI(id))
    )
    
    message.success(`${selectedIds.value.length} resident(s) deleted successfully`)
    selectedIds.value = []
    showDeleteModal.value = false
    loadResidents() // Reload the table
  } catch (error) {
    console.error('Failed to delete residents:', error)
    message.error('Failed to delete some residents')
  }
}

async function handleDeleteSingle(id) {
  pendingDeleteId.value = id
  showSingleDeleteModal.value = true
}

async function confirmSingleDelete() {
  try {
    await deleteResidentAPI(pendingDeleteId.value)
    message.success('Resident deleted successfully')
    showSingleDeleteModal.value = false
    pendingDeleteId.value = null
    loadResidents()
  } catch (error) {
    console.error('Failed to delete resident:', error)
    message.error('Failed to delete resident')
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
            if (!selectedIds.value.includes(row.id)) {
              selectedIds.value.push(row.id)
            }
          } else {
            selectedIds.value = selectedIds.value.filter(id => id !== row.id)
          }
        }
      })
    }
  },
  {
    title: '#',
    key: 'index',
    width: 50,
    render(_row, index) {
      return index + 1
    }
  },
  {
    title: 'Full Name',
    key: 'full_name',
    minWidth: 100
  },
  {
    title: 'Phone Number',
    key: 'phone_number',
    width: 150,
    render(row) {
      return row.phone_number || 'N/A'
    }
  },
  {
    title: 'RFID No.',
    key: 'rfid_no',
    width: 150,
    render(row) {
      return row.rfid_no || 'N/A'
    }
  },
  {
    title: 'Current Address',
    key: 'current_address',
    minWidth: 250,
    render(row) {
      return row.current_address || 'N/A'
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
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Residents Information Management" />
        <p class="text-sm text-gray-500 mt-1">Manage Residents Information</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-3">
        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- Filter Button -->
        <button
          @click="showFilterModal = true"
          class="p-2 border border-gray-400 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <FunnelIcon class="w-5 h-5 text-gray-700" />
        </button>

        <!-- Bulk Delete Button -->
        <div class="flex items-center gap-1.5">
          <button
            @click="requestBulkDelete"
            :disabled="selectionState === 'none'"
            class="p-2 border border-red-400 rounded-lg transition-colors"
            :class="
              selectionState === 'none'
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-red-50'
            "
          >
            <TrashIcon class="w-5 h-5 text-red-500" />
          </button>
          <span
            v-if="selectedCount > 0"
            class="text-xs font-medium text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full"
          >
            {{ selectedCount }} selected
          </span>
        </div>

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
              :class="
                selectionState !== 'none'
                  ? 'bg-blue-600 border-blue-600'
                  : 'border-gray-400'
              "
            >
              <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
              <CheckIcon v-if="selectionState === 'all'" class="w-3 h-3 text-white" />
            </div>
          </button>
        </div>

        <!-- Register Button -->
        <button
          @click="openAddModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          Register
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200">
      <n-data-table 
        :columns="columns" 
        :data="filteredResidents" 
        :loading="loading"
        :bordered="false"
      />
    </div>

    <!-- Modals -->
    <ResidentModal
      :show="showResidentModal"
      :mode="modalMode"
      :resident-id="currentResident?.id"
      @close="handleModalClose"
      @saved="handleResidentSaved"
    />

    <ConfirmModal
      :show="showDeleteModal"
      :title="`Delete ${selectedIds.length} resident(s)?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />

    <ConfirmModal
      :show="showSingleDeleteModal"
      title="Delete this resident?"
      description="This will permanently remove the resident and all associated data. This action cannot be undone."
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmSingleDelete"
      @cancel="showSingleDeleteModal = false; pendingDeleteId = null"
    />
  </div>
</template>