<script setup>
import { ref, onMounted, h } from 'vue'
import { NDataTable, NInput, NButton, NModal, NSelect, NCheckbox, useMessage } from 'naive-ui'
import PageTitle from '@/components/shared/PageTitle.vue'
import Templates from './Templates.vue'
import requestTypesApi from '@/api/requestTypes'
import FieldEditor from './FieldEditor.vue'

const message = useMessage()

// ======================================
// Services Data
// ======================================
const services = ref([])
const editingId = ref(null)
const showTemplates = ref(false)

const newService = ref({
  request_type_name: '',
  description: '',
  price: 0,
  available: true,
})

const pagination = { pageSize: 8 }

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

  try {
    await requestTypesApi.create({
      ...newService.value,
      fields: newService.value.fields || []
    })
    message.success('Service added!')
    newService.value = { request_type_name: '', description: '', price: 0, available: true, fields: [] }
    fetchServices()
  } catch (err) {
    console.error(err)
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
    title: 'Available',
    key: 'available',
    width: 120,
    render(row) {
      if (editingId.value === row.id) {
        return h(NCheckbox, {
          checked: row.available, 
          onUpdateChecked(v) { row.available = v } 
        })
      }
      return row.available ? 'Yes' : 'No'
    }
  },
  { title: 'Status', key: 'status', width: 100 },
  {
    title: 'Actions',
    key: 'actions',
    width: 400,
    render(row) {
      if (editingId.value === row.id) {
        return [
          h(NButton, { type: 'success', size: 'small', onClick: () => updateService(row) }, { default: () => 'Save' }),
          h(NButton, { type: 'default', size: 'small', onClick: () => (editingId.value = null), style: 'margin-left: 8px;' }, { default: () => 'Cancel' }),
        ]
      }

      return [
        h(NButton, { type: 'primary', size: 'small', onClick: () => startEdit(row.id) }, { default: () => 'Edit' }),
        h(NButton, { type: 'error', size: 'small', onClick: () => deleteService(row.id), style: 'margin-left: 8px;' }, { default: () => 'Delete' }),
        h(NButton, { type: 'info', size: 'small', onClick: () => editFields(row), style: 'margin-left: 8px;' }, { default: () => 'Configure Fields' }),
      ]
    }
  }
]

onMounted(fetchServices)
</script>

<template>
  <div class="p-6 bg-white min-h-screen rounded-md w-full space-y-5">
    <!------------------------ Header ------------------------>
    <div class="flex items-center justify-between">
      <PageTitle title="Document Services Management" />
      <button
        @click="showTemplates = !showTemplates"
        :class="[
          'px-4 py-2 rounded-md font-medium text-sm transition',
          showTemplates
            ? 'bg-[#0957FF] text-white shadow-md'
            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
        ]"
      >
        Templates
      </button> 
    </div>

    <div v-if="!showTemplates" class="bg-white p-6 rounded-lg shadow-md">
      <div class="flex items-center space-x-3 mb-6">
        <n-input v-model:value="newService.request_type_name" placeholder="Service Name" style="width: 200px" />
        <n-input v-model:value="newService.description" placeholder="Description" style="width: 250px" />
        <n-input v-model:value="newService.price" type="number" placeholder="Price" style="width: 120px" />
        <NCheckbox v-model:checked="newService.available">Available</NCheckbox>
        <n-button type="primary" @click="addService">Add</n-button>
      </div>

      <n-data-table
        :columns="columns"
        :data="services"
        :bordered="true"
        :pagination="pagination"
      />

    </div>

    <div v-else>
      <Templates />
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