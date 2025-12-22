<script setup>
import { ref, onMounted, h } from 'vue'
import { NDataTable, NInput, NButton, NCheckbox, useMessage, NUpload, NUploadDragger } from 'naive-ui'
import { PencilSquareIcon, TrashIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import PageTitle from '@/components/shared/PageTitle.vue'
import requestTypesApi from '@/api/requestTypes'
import FieldEditor from './FieldEditor.vue'

const message = useMessage()

// ======================================
// Services Data
// ======================================
const services = ref([])
const editingId = ref(null)
const showAddForm = ref(false)
const searchQuery = ref('')
const uploadedFile = ref(null)

function handleUpload({ file }) {
  uploadedFile.value = file
}

const newService = ref({
  request_type_name: '',
  description: '',
  price: 0,
  available: true,
})

// ======================================
// Fetch Services
// ======================================
async function fetchServices() {
  try {
    const res = await requestTypesApi.getAll()
    services.value = res.data
  } catch (err) {
    console.error(err)
    message.error('Failed to load services.')
  }
}

// ======================================
// CRUD Handlers
// ======================================
async function addService() {
  if (!newService.value.request_type_name.trim()) {
    return message.warning('Please enter a service name.')
  }

  const formData = new FormData()
  formData.append('request_type_name', newService.value.request_type_name)
  formData.append('description', newService.value.description)
  formData.append('price', newService.value.price)
  formData.append('available', newService.value.available)

  if (uploadedFile.value) {
    formData.append('file', uploadedFile.value.file)
  }

  try {
    await requestTypesApi.create(formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    message.success('Service added!')
    showAddForm.value = false
    uploadedFile.value = null
    newService.value = { request_type_name: '', description: '', price: 0, available: true }
    fetchServices()
  } catch (err) {
    message.error('Failed to add service.')
  }
}

async function updateService(service) {
  try {
    await requestTypesApi.update(service.id, {
      ...service,
      fields: service.fields || []
    })
    editingId.value = null
    message.success('Service updated!')
    fetchServices()
  } catch (err) {
    console.error(err)
    message.error('Failed to update service.')
  }
}

async function deleteService(id) {
  if (!confirm('Are you sure you want to delete this service?')) return

  try {
    await requestTypesApi.delete(id)
    message.success('Service deleted!')
    fetchServices()
  } catch (err) {
    console.error(err)
    message.error('Failed to delete service.')
  }
}

function startEdit(id) {
  editingId.value = id
}

// ======================================
// Download Handler
// ======================================
function downloadTemplate(service) {
  // Implement your download logic here
  message.info(`Downloading template for ${service.request_type_name}`)
  // Example: window.open(`/api/templates/${service.id}/download`, '_blank')
}

// ======================================
// Field Configuration Modal
// ======================================
const editingFields = ref(null)
const showFieldModal = ref(false)

function editFields(service) {
  editingFields.value = {
    fields: JSON.parse(JSON.stringify(service.fields || [])), // clone array
    serviceId: service.id
  }
  showFieldModal.value = true
}

function saveFields(updatedFields, serviceId) {
  const service = services.value.find(s => s.id === serviceId)
  if (service) {
    service.fields = updatedFields
    updateService(service)
  }
  showFieldModal.value = false
}

// ======================================
// Table Columns
// ======================================
const columns = [
  { title: 'ID', key: 'id', width: 70 },
  {
    title: 'Name',
    key: 'request_type_name',
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.request_type_name,
          onUpdateValue(v) { row.request_type_name = v }
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
          onUpdateValue(v) { row.description = v }
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
          onUpdateValue(v) { row.price = Number(v) }
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
      const isAvailable = row.available
      return h('span', {
        class: `px-3 py-1 rounded-full text-xs font-medium ${
          isAvailable 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`
      }, isAvailable ? 'Available' : 'Not Available')
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 300,
    render(row) {
      if (editingId.value === row.id) {
        return [
          h(NButton, { type: 'success', size: 'small', onClick: () => updateService(row) }, { default: () => 'Save' }),
          h(NButton, { type: 'default', size: 'small', onClick: () => (editingId.value = null), style: 'margin-left: 8px;' }, { default: () => 'Cancel' }),
        ]
      }

      return h('div', { class: 'flex gap-2 items-center' }, [
        h('button', { 
          onClick: () => startEdit(row.id),
          class: 'p-1.5 text-yellow-600 hover:bg-yellow-50 rounded transition',
          title: 'Edit'
        }, [
          h(PencilSquareIcon, { class: 'w-5 h-5' })
        ]),
        h('button', { 
          onClick: () => deleteService(row.id),
          class: 'p-1.5 text-red-600 hover:bg-red-50 rounded transition',
          title: 'Delete'
        }, [
          h(TrashIcon, { class: 'w-5 h-5' })
        ]),
        h(NButton, { type: 'info', size: 'small', onClick: () => editFields(row) }, { default: () => 'Configure Fields' }),
        h(NButton, { type: 'success', size: 'small', onClick: () => downloadTemplate(row) }, { default: () => 'Download' }),
      ])
    }
  }
]

onMounted(fetchServices)
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!------------------------ Header ------------------------>
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Document Services Management" />
        <p class="text-sm text-gray-500 mt-1">Manage Document Services and Templates</p>
      </div>
      
      <div class="flex items-center gap-3">
        <n-input 
          v-model:value="searchQuery" 
          placeholder="Search" 
          style="width: 250px"
          clearable
        />
        <button 
          class="p-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
          title="Delete Selected"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
        <button 
          class="p-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
          title="Select"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
        <button
          @click="showAddForm = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <!------------------------ Add Form ------------------------>
    <div v-if="showAddForm" class="bg-[#F0F5FF] p-6 0 mb-3 rounded-lg border border-[#0957FF] relative">
      <button 
        @click="showAddForm = false"
        class="absolute top-4 right-4 p-1 hover:bg-gray-200 rounded transition"
      >
        <XMarkIcon class="w-5 h-5 text-gray-600" />
      </button>
      
      <div class="grid grid-cols-[2fr_1fr_1fr_2fr] gap-4 items-end">
        <!------------------------ TEXT ------------------------>
        <div class="flex flex-col gap-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Document Name</label>
            <n-input v-model:value="newService.request_type_name" placeholder="Enter name" />
          </div>
          
          <div>
            <label class="block text-sm text-gray-600 mb-1">Description</label>
            <n-input v-model:value="newService.description" placeholder="Enter description" />
          </div>
        </div>

        <!------------------------ PRICE ------------------------>
        <div>
          <label class="block text-sm text-gray-600 mb-1">Price</label>
          <n-input v-model:value="newService.price" type="number" placeholder="Enter price" />
        </div>
        
        <NCheckbox v-model:checked="newService.available" class="place-self-center self-end">Available</NCheckbox>

        <div class="w-full">
          <n-upload
            :show-file-list="true"
            :default-upload="false"
            :on-change="handleUpload"
            accept=".docx,.pdf"
            class="w-full"
          >
            <n-upload-dragger>
              <div class="text-gray-500 text-sm">
                Click or drag file here to upload
              </div>
            </n-upload-dragger>
          </n-upload>
        </div>
      </div>
      
      <div class="flex justify-end gap-3 mt-6">
        <n-button @click="showAddForm = false">Cancel</n-button>
        <n-button type="primary" @click="addService">Add Document Type</n-button>
      </div>
    </div>

    <!------------------------ Data Table ------------------------>
    <div class="overflow-y-auto bg-white rounded-lg border border-gray-200">
      <n-data-table
        :columns="columns"
        :data="services"
        :bordered="false"
      />
    </div>
    
    <!----------------- Field Editor Modal ----------------->
    <FieldEditor
      :show="showFieldModal"
      :fields-data="editingFields?.fields"
      @close="showFieldModal = false"
      @saved="saveFields"
      :service-id="editingFields?.serviceId"
    />
  </div>
</template>