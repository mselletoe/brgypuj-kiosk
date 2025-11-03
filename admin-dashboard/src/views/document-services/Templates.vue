<script setup>
import { ref, onMounted, h } from 'vue'
import api from '@/api/api'
import {
  NDataTable,
  NInput,
  NButton,
  NSelect,
  NModal,
  NForm,
  NFormItem,
  useMessage,
  NUpload,
  NUploadDragger,
} from 'naive-ui'

const message = useMessage()
const templates = ref([])
const requestTypes = ref([])
const file = ref(null)
const editFile = ref(null)
const showEditModal = ref(false)
const selectedTemplate = ref(null)

const newTemplate = ref({
  template_name: '',
  description: '',
  request_type_id: null,
})

const editTemplate = ref({
  id: null,
  template_name: '',
  description: '',
  request_type_id: null,
})

const pagination = { pageSize: 10 }

// -------------------- FETCH --------------------
async function fetchTemplates() {
  const res = await api.get('/templates')
  templates.value = res.data
}

async function fetchRequestTypes() {
  const res = await api.get('/request-types')
  requestTypes.value = res.data.map(r => ({
    label: r.request_type_name,
    value: r.id,
  }))
}

// -------------------- UPLOAD --------------------
async function handleUpload({ file: uploadedFile }) {
  file.value = uploadedFile
}

async function addTemplate() {
  if (!newTemplate.value.template_name || !file.value) {
    return message.warning('Please fill all fields and attach a file.')
  }

  const formData = new FormData()
  formData.append('template_name', newTemplate.value.template_name)
  formData.append('description', newTemplate.value.description)
  formData.append('request_type_id', newTemplate.value.request_type_id)
  formData.append('file', file.value.file)

  await api.post('/templates', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  message.success('Template uploaded successfully!')
  newTemplate.value = { template_name: '', description: '', request_type_id: null }
  file.value = null
  fetchTemplates()
}

// -------------------- DELETE --------------------
async function deleteTemplate(id) {
  if (confirm('Are you sure you want to delete this template?')) {
    await api.delete(`/templates/${id}`)
    message.success('Template deleted!')
    fetchTemplates()
  }
}

// -------------------- PREVIEW --------------------
function previewTemplate(id) {
  window.open(`${import.meta.env.VITE_API_BASE_URL}/templates/${id}/download`, '_blank')
}

// -------------------- EDIT --------------------
function openEditModal(row) {
  selectedTemplate.value = row
  editTemplate.value = { ...row }
  showEditModal.value = true
}

async function handleEditUpload({ file: uploadedFile }) {
  editFile.value = uploadedFile
}

async function saveTemplateEdits() {
  const formData = new FormData()
  if (editTemplate.value.template_name)
    formData.append('template_name', editTemplate.value.template_name)
  if (editTemplate.value.description)
    formData.append('description', editTemplate.value.description)
  if (editTemplate.value.request_type_id)
    formData.append('request_type_id', editTemplate.value.request_type_id)
  if (editFile.value)
    formData.append('file', editFile.value.file)

  await api.put(`/templates/${editTemplate.value.id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  message.success('Template updated successfully!')
  showEditModal.value = false
  fetchTemplates()
}

// -------------------- TABLE --------------------
const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: 'Template Name', key: 'template_name' },
  { title: 'Description', key: 'description' },
  {
    title: 'Linked Request Type',
    key: 'request_type_name',
    render(row) {
      return row.request_type_name || '—'
    },
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 220,
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            class: 'mr-2',
            onClick: () => previewTemplate(row.id),
          },
          { default: () => 'Preview' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'warning',
            class: 'mr-2',
            onClick: () => openEditModal(row),
          },
          { default: () => 'Edit' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'error',
            onClick: () => deleteTemplate(row.id),
          },
          { default: () => 'Delete' }
        ),
      ]
    },
  },
]

onMounted(() => {
  fetchTemplates()
  fetchRequestTypes()
})
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-2">Manage Document Templates</h2>
    <p class="mb-12 text-gray-600">
      Add, view, and manage document templates used for various request types.
    </p>

    <!-- Upload Form -->
    <div
      class="border border-gray-300 rounded-xl p-6 grid grid-cols-1 md:grid-cols-6 gap-3 items-start w-full mb-10"
    >
      <n-input v-model:value="newTemplate.template_name" placeholder="Template Name" class="w-full" />
      <n-input v-model:value="newTemplate.description" placeholder="Description" class="w-full" />
      <n-select
        v-model:value="newTemplate.request_type_id"
        :options="requestTypes"
        placeholder="Link to Request Type"
        class="w-full"
      />
      <div class="md:col-span-2 w-full">
        <n-upload
          :show-file-list="true"
          :default-upload="false"
          :on-change="handleUpload"
          accept=".docx,.pdf"
          class="w-full"
        >
          <n-upload-dragger>
            <div class="text-gray-500 text-sm">Click or drag file here to upload</div>
          </n-upload-dragger>
        </n-upload>
      </div>
      <n-button type="primary" @click="addTemplate" class="w-full">Upload</n-button>
    </div>

    <!-- Templates Table -->
    <n-data-table
      :columns="columns"
      :data="templates"
      :bordered="true"
      :pagination="pagination"
    />

    <!-- Edit Modal -->
    <n-modal v-model:show="showEditModal" preset="dialog" title="Edit Template">
      <n-form label-placement="top" class="space-y-3">
        <n-form-item label="Template Name">
          <n-input v-model:value="editTemplate.template_name" />
        </n-form-item>
        <n-form-item label="Description">
          <n-input v-model:value="editTemplate.description" />
        </n-form-item>
        <n-form-item label="Linked Request Type">
          <n-select
            v-model:value="editTemplate.request_type_id"
            :options="requestTypes"
            placeholder="Select Request Type"
          />
        </n-form-item>
        <n-form-item label="Replace File (optional)">
          <n-upload
            :show-file-list="true"
            :default-upload="false"
            :on-change="handleEditUpload"
            accept=".docx,.pdf"
          >
            <n-upload-dragger>
              <div class="text-gray-500 text-sm">Click or drag file to replace</div>
            </n-upload-dragger>
          </n-upload>
        </n-form-item>
      </n-form>

      <template #action>
        <div class="flex justify-end gap-3">
          <n-button @click="showEditModal = false">Cancel</n-button>
          <n-button type="primary" @click="saveTemplateEdits">Save Changes</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>