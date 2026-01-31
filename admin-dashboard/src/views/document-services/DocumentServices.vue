<script setup>
import { ref, onMounted, h, computed, watch } from 'vue'
import { NDataTable, NInput, NButton, NCheckbox, useMessage, NUpload, NUploadDragger } from 'naive-ui'
import { PencilSquareIcon, TrashIcon, XMarkIcon, CheckIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import FieldEditor from './FieldEditor.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getDocumentTypes,
  createDocumentType,
  updateDocumentType,
  deleteDocumentType,
  uploadDocumentTemplate,
  downloadDocumentTemplate
} from '@/api/documentService'

const message = useMessage()

// ======================================
// State Management
// ======================================
const services = ref([])
const editingId = ref(null)
const showAddForm = ref(false)
const searchQuery = ref('')
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)
const selectedIds = ref([])
const isBulkDelete = ref(false)

const newService = ref({
  request_type_name: '',
  description: '',
  price: 0,
  available: true,
  fields: []
})

// ======================================
// Fetch Services
// ======================================
async function fetchServices() {
  try {
    const { data } = await getDocumentTypes()
    services.value = data.map(d => ({
      id: d.id,
      request_type_name: d.doctype_name,
      description: d.description,
      price: Number(d.price),
      available: d.is_available,
      fields: d.fields || [],
      has_template: d.has_template || false
    }))
  } catch (error) {
    console.error(error)
    message.error('Failed to fetch document types.')
  }
}

// ======================================
// CRUD Handlers
// ======================================
async function addService() {
  if (!newService.value.request_type_name.trim()) {
    return message.warning('Please enter a service name.')
  }

  try {
    const { data } = await createDocumentType({
      doctype_name: newService.value.request_type_name,
      description: newService.value.description,
      price: newService.value.price,
      fields: newService.value.fields || [],
      is_available: newService.value.available
    })

    services.value.push({
      id: data.id,
      request_type_name: data.doctype_name,
      description: data.description,
      price: Number(data.price),
      available: data.is_available,
      fields: data.fields || [],
      has_template: false
    })

    message.success('Document type created successfully. You can now upload a template.')

    showAddForm.value = false
    newService.value = {
      request_type_name: '',
      description: '',
      price: 0,
      available: true,
      fields: []
    }
  } catch (error) {
    console.error('Full error:', error)
    console.error('Error response:', error.response)
    
    const errorMsg = error.response?.data?.detail || 'Failed to add document type.'
    message.error(errorMsg)
  }
}

async function updateService(service) {
  try {
    const { data } = await updateDocumentType(service.id, {
      doctype_name: service.request_type_name,
      description: service.description,
      price: service.price,
      is_available: service.available,
      fields: service.fields
    })

    const idx = services.value.findIndex(s => s.id === service.id)
    if (idx !== -1) {
      services.value[idx] = {
        id: data.id,
        request_type_name: data.doctype_name,
        description: data.description,
        price: Number(data.price),
        available: data.is_available,
        fields: data.fields || [],
        has_template: services.value[idx].has_template
      }
    }

    editingId.value = null
    message.success('Service updated successfully.')
  } catch (err) {
    console.error(err)
    message.error('Update failed.')
  }
}

// ======================================
// Toggle Availability
// ======================================
async function toggleAvailability(service) {
  try {
    const newStatus = !service.available
    
    const { data } = await updateDocumentType(service.id, {
      is_available: newStatus
    })

    service.available = data.is_available
    message.success(`Service ${newStatus ? 'enabled' : 'disabled'} successfully.`)
  } catch (err) {
    console.error(err)
    message.error('Failed to update availability.')
  }
}

// ======================================
// Delete Logic (Single & Bulk)
// ======================================
function requestDelete(id) {
  deleteTargetId.value = id
  isBulkDelete.value = false
  showDeleteModal.value = true
}

function bulkDelete() {
  if (!selectedIds.value.length) return
  isBulkDelete.value = true
  showDeleteModal.value = true
}

async function confirmDelete() {
  try {
    if (isBulkDelete.value) {
      await Promise.all(selectedIds.value.map(id => deleteDocumentType(id)))
      services.value = services.value.filter(s => !selectedIds.value.includes(s.id))
      message.success(`${selectedIds.value.length} service(s) deleted successfully.`)
      selectedIds.value = []
    } else {
      await deleteDocumentType(deleteTargetId.value)
      services.value = services.value.filter(s => s.id !== deleteTargetId.value)
      message.success('Service deleted successfully.')
    }
  } catch (err) {
    console.error('Delete error:', err)
    console.error('Error response:', err.response)
    const errorMsg = err.response?.data?.detail || 'Delete failed.'
    message.error(errorMsg)
  } finally {
    deleteTargetId.value = null
    showDeleteModal.value = false
  }
}

function cancelDelete() {
  showDeleteModal.value = false
  deleteTargetId.value = null
}

// ======================================
// Selection Logic
// ======================================
const totalCount = computed(() => filteredServices.value.length)
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
    selectedIds.value = filteredServices.value.map(s => s.id)
  }
}

// ======================================
// Template Upload/Download
// ======================================
async function handleUploadTemplate(service) {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.pdf,.docx'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const allowed = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    if (!allowed.includes(file.type)) {
      message.error('Only PDF or DOCX files are allowed.')
      return
    }

    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      message.error('File size must not exceed 10MB.')
      return
    }

    try {
      await uploadDocumentTemplate(service.id, file)
      service.has_template = true
      message.success('Template uploaded successfully.')
    } catch (err) {
      console.error(err)
      message.error('Failed to upload template.')
    }
  }

  input.click()
}

async function handleDownload(service) {
  try {
    await downloadDocumentTemplate(service.id, service.request_type_name)
    message.success('Download started.')
  } catch (err) {
    console.error(err)
    message.error('Failed to download template.')
  }
}

// ======================================
// Field Editor
// ======================================
const editingFields = ref(null)
const showFieldModal = ref(false)

function editFields(service) {
  editingFields.value = {
    fields: JSON.parse(JSON.stringify(service.fields || [])),
    serviceId: service.id
  }
  showFieldModal.value = true
}

async function saveFields(updatedFields, serviceId) {
  const service = services.value.find(s => s.id === serviceId)
  if (!service) return

  try {
    await updateDocumentType(serviceId, {
      doctype_name: service.request_type_name,
      description: service.description,
      price: service.price,
      is_available: service.available,
      fields: updatedFields
    })

    service.fields = updatedFields
    message.success('Fields updated successfully.')
  } catch (err) {
    console.error(err)
    message.error('Failed to update fields.')
  } finally {
    showFieldModal.value = false
  }
}

// ======================================
// Filtering & Search
// ======================================
const filteredServices = computed(() => {
  const filtered = !searchQuery.value
    ? services.value
    : services.value.filter(s =>
        s.request_type_name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )

  // Clear editing if filtered out
  if (editingId.value && !filtered.find(s => s.id === editingId.value)) {
    editingId.value = null
  }

  return filtered
})

// Clear selections when search changes
watch(searchQuery, () => {
  selectedIds.value = []
})

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
    title: 'ID',
    key: 'id',
    width: 70
  },
  {
    title: 'Name',
    key: 'request_type_name',
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.request_type_name,
          onUpdateValue(v) {
            row.request_type_name = v
          }
        })
      }
      return row.request_type_name
    }
  },
  {
    title: 'Description',
    key: 'description',
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.description,
          onUpdateValue(v) {
            row.description = v
          }
        })
      }
      return row.description
    }
  },
  {
    title: 'Price',
    key: 'price',
    width: 120,
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.price,
          type: 'number',
          onUpdateValue(v) {
            row.price = Number(v)
          }
        })
      }
      return `₱${parseFloat(row.price).toFixed(2)}`
    }
  },
  {
    title: 'Status',
    key: 'status',
    width: 140,
    render(row) {
      return h('div', { class: 'flex items-center gap-2' }, [
        h(
          'button',
          {
            onClick: () => toggleAvailability(row),
            class: `px-3 py-1 rounded-full text-xs font-medium cursor-pointer transition ${
              row.available 
                ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`
          },
          row.available ? 'Available' : 'Not Available'
        )
      ])
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 300,
    render(row) {
      if (editingId.value === row.id) {
        return h('div', { class: 'flex gap-2' }, [
          h(
            NButton,
            {
              type: 'success',
              size: 'small',
              onClick: () => updateService(row)
            },
            { default: () => 'Save' }
          ),
          h(
            NButton,
            {
              type: 'default',
              size: 'small',
              onClick: () => (editingId.value = null)
            },
            { default: () => 'Cancel' }
          )
        ])
      }

      return h('div', { class: 'flex gap-2 items-center' }, [
        h(
          'button',
          {
            onClick: () => (editingId.value = row.id),
            class: 'p-1.5 text-yellow-600 hover:bg-yellow-50 rounded transition'
          },
          [h(PencilSquareIcon, { class: 'w-5 h-5' })]
        ),
        h(
          'button',
          {
            onClick: () => requestDelete(row.id),
            class: 'p-1.5 text-red-600 hover:bg-red-50 rounded transition'
          },
          [h(TrashIcon, { class: 'w-5 h-5' })]
        ),
        h(
          NButton,
          {
            type: 'info',
            size: 'small',
            onClick: () => editFields(row)
          },
          { default: () => 'Fields' }
        ),
        h(
          NButton,
          {
            type: 'warning',
            size: 'small',
            onClick: () => handleUploadTemplate(row)
          },
          { default: () => row.has_template ? 'Replace' : 'Upload' }
        ),
        row.has_template
          ? h(
              NButton,
              {
                type: 'success',
                size: 'small',
                onClick: () => handleDownload(row)
              },
              { default: () => 'Download' }
            )
          : null
      ].filter(Boolean))
    }
  }
])

onMounted(fetchServices)
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Document Services Management" />
        <p class="text-sm text-gray-500 mt-1">
          Create, edit, and configure official barangay document templates and pricing.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <n-input
          v-model:value="searchQuery"
          placeholder="Search"
          style="width: 250px"
          clearable
        />

        <button
          @click="bulkDelete"
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

        <button
          @click="showAddForm = true"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add
        </button>
      </div>
    </div>

    <div
      v-if="showAddForm"
      class="bg-[#F0F5FF] p-6 mb-3 rounded-lg border border-[#0957FF] relative"
    >
      <button
        @click="showAddForm = false"
        class="absolute top-4 right-4 p-1 hover:bg-gray-200 rounded"
      >
        <XMarkIcon class="w-5 h-5 text-gray-600" />
      </button>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Document Name</label>
          <n-input
            v-model:value="newService.request_type_name"
            placeholder="Enter name"
          />
        </div>
        
        <div>
          <label class="block text-sm text-gray-600 mb-1">Description</label>
          <n-input
            v-model:value="newService.description"
            placeholder="Enter description"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Price (₱)</label>
          <n-input 
            v-model:value="newService.price" 
            type="number" 
            placeholder="0.00"
            min="0"
            step="0.01"
          />
        </div>

        <div class="flex items-end">
          <NCheckbox v-model:checked="newService.available">
            Available for Residents
          </NCheckbox>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <n-button @click="showAddForm = false">Cancel</n-button>
        <n-button 
          type="primary" 
          @click="addService"
        >
          Add Document Type
        </n-button>
      </div>
    </div>

    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200">
      <n-data-table :columns="columns" :data="filteredServices" :bordered="false" />
    </div>

    <FieldEditor
      :show="showFieldModal"
      :fields-data="editingFields?.fields"
      @close="showFieldModal = false"
      @saved="saveFields"
      :service-id="editingFields?.serviceId"
    />
  </div>

  <ConfirmModal
    :show="showDeleteModal"
    :title="
      isBulkDelete
        ? `Delete ${selectedIds.length} service(s)?`
        : 'Delete this service?'
    "
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />
</template>