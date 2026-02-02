<script setup>
import { ref, computed, h, watch } from 'vue'
import { NDataTable, NInput, NButton, NCheckbox, useMessage } from 'naive-ui'
import { FunnelIcon, TrashIcon, CheckIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentModal from './ResidentModal.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

const message = useMessage()

// ======================================
// State Management
// ======================================
const residents = ref([
  {
    id: 1,
    firstName: 'First Name',
    middleName: 'Middle Name',
    lastName: 'Last Name',
    suffix: 'Suffix',
    phoneNumber: '09123456789',
    rfid: 'RFID No.',
    currentAddress: 'House No./St., Purok X',
    status: 'Active'
  },
  {
    id: 2,
    firstName: 'First Name',
    middleName: 'Middle Name',
    lastName: 'Last Name',
    suffix: 'Suffix',
    phoneNumber: '09123456789',
    rfid: 'RFID No.',
    currentAddress: 'House No./St., Purok X',
    status: 'Active'
  }
])

const searchQuery = ref('')
const selectedIds = ref([])
const showDeleteModal = ref(false)
const showFilterModal = ref(false)
const showResidentModal = ref(false)
const currentResident = ref(null)
const modalMode = ref('add')

// ======================================
// Selection Logic
// ======================================
const filteredResidents = computed(() => {
  if (!searchQuery.value) return residents.value
  
  const query = searchQuery.value.toLowerCase()
  return residents.value.filter(r => 
    r.firstName.toLowerCase().includes(query) ||
    r.middleName.toLowerCase().includes(query) ||
    r.lastName.toLowerCase().includes(query) ||
    r.phoneNumber.includes(query) ||
    r.rfid.toLowerCase().includes(query)
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
  currentResident.value = { ...resident }
  showResidentModal.value = true
}

function handleSaveResident(residentData) {
  if (modalMode.value === 'add') {
    // Add new resident
    const newId = Math.max(...residents.value.map(r => r.id), 0) + 1
    residents.value.push({
      id: newId,
      ...residentData
    })
    message.success('Resident registered successfully')
  } else {
    // Update existing resident
    const index = residents.value.findIndex(r => r.id === currentResident.value.id)
    if (index !== -1) {
      residents.value[index] = {
        ...residents.value[index],
        ...residentData
      }
      message.success('Resident updated successfully')
    }
  }
  showResidentModal.value = false
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

function confirmDelete() {
  residents.value = residents.value.filter(r => !selectedIds.value.includes(r.id))
  message.success(`${selectedIds.value.length} resident(s) deleted successfully`)
  selectedIds.value = []
  showDeleteModal.value = false
}

function deleteResident(id) {
  residents.value = residents.value.filter(r => r.id !== id)
  message.success('Resident deleted successfully')
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
    title: '',
    key: 'id',
    width: 60,
    render(row) {
      return row.id
    }
  },
  {
    title: 'First Name Middle Name Last Name Suffix',
    key: 'fullName',
    render(row) {
      return `${row.firstName} ${row.middleName} ${row.lastName} ${row.suffix}`
    }
  },
  {
    title: 'Phone Number',
    key: 'phoneNumber',
    width: 150
  },
  {
    title: 'RFID',
    key: 'rfid',
    width: 120
  },
  {
    title: 'Current Address',
    key: 'currentAddress',
    width: 200
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 150,
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
            onClick: () => deleteResident(row.id),
            class: 'p-1.5 text-red-600 hover:bg-red-50 rounded transition'
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
        <PageTitle title="Residents Management" />
        <p class="text-sm text-gray-500 mt-1">Manage Residents Information</p>
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
          @click="showFilterModal = true"
          class="p-2 border border-gray-400 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <FunnelIcon class="w-5 h-5 text-gray-700" />
        </button>

        <!-- Bulk Delete Button -->
        <button
          @click="requestBulkDelete"
          :disabled="selectionState === 'none'"
          class="p-2 border border-red-700 rounded-lg transition-colors"
          :class="
            selectionState === 'none'
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-red-50'
          "
        >
          <TrashIcon class="w-5 h-5 text-red-700" />
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
        :bordered="false"
      />
    </div>

    <!-- Modals -->
    <ResidentModal
      :show="showResidentModal"
      :mode="modalMode"
      :resident="currentResident"
      @close="showResidentModal = false"
      @save="handleSaveResident"
    />

    <ConfirmModal
      :show="showDeleteModal"
      :title="`Delete ${selectedIds.length} resident(s)?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>