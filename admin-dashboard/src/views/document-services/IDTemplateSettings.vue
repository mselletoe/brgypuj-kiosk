<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import {
  NButton, NUpload, NUploadDragger, NTag,
  NInput, NSelect, NCheckbox, NSpin, useMessage
} from 'naive-ui'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  TrashIcon,
  PlusIcon,
  InformationCircleIcon,
} from '@heroicons/vue/24/outline'
import { v4 as uuidv4 } from 'uuid'
import PageTitle from '@/components/shared/PageTitle.vue'
import {
  getDocumentTypes,
  createDocumentType,
  updateDocumentType,
  uploadDocumentTemplate,
  downloadDocumentTemplate,
} from '@/api/documentService'

const message = useMessage()

// ======================================
// State
// ======================================
const loading   = ref(true)
const saving    = ref(false)
const uploading = ref(false)
const idDocType = ref(null)

// Inline field editing
const localFields = ref([])

// ======================================
// Fixed placeholders (date fields removed)
// ======================================
const FIXED_FIELDS = [
  { name: 'last_name',      label: 'Last Name',       source: 'Resident DB / Manual' },
  { name: 'first_name',     label: 'First Name',      source: 'Resident DB / Manual' },
  { name: 'middle_name',    label: 'Middle Name',     source: 'Resident DB / Manual' },
  { name: 'birthdate',      label: 'Birthdate',       source: 'Resident DB / Manual' },
  { name: 'address',        label: 'Address',         source: 'Resident DB / Manual' },
  { name: 'contact_number', label: 'Contact Number',  source: 'Resident DB / Manual' },
  { name: 'photo',          label: 'Photo',           source: 'Camera Capture'       },
  { name: 'brgy_id_number', label: 'Barangay ID No.', source: 'Assigned on Release'  },
]

// ======================================
// Load
// ======================================
onMounted(loadIDDocType)

async function loadIDDocType() {
  loading.value = true
  try {
    const { data } = await getDocumentTypes()
    const found = data.find(t => t.is_id_application === true)
    idDocType.value = found || null
    localFields.value = JSON.parse(JSON.stringify(found?.fields || []))
  } catch (err) {
    console.error(err)
    message.error('Failed to load ID template settings.')
  } finally {
    loading.value = false
  }
}

// ======================================
// Ensure ID doctype row exists
// ======================================
async function ensureIDDocType() {
  if (idDocType.value) return idDocType.value
  const { data } = await createDocumentType({
    doctype_name:      'ID Application',
    description:       'Barangay Identification Card application template.',
    price:             0,
    fields:            [],
    is_available:      true,
    is_id_application: true,
  })
  idDocType.value = data
  return data
}

// ======================================
// Template Upload / Download
// ======================================
async function handleFileUpload({ file }) {
  if (!file?.file) return
  const raw = file.file
  if (!raw.name.endsWith('.docx')) {
    message.warning('Only .docx files are accepted.')
    return false
  }
  uploading.value = true
  try {
    const docType = await ensureIDDocType()
    await uploadDocumentTemplate(docType.id, raw)
    message.success('Template uploaded successfully.')
    await loadIDDocType()
  } catch (err) {
    console.error(err)
    message.error('Upload failed. Please try again.')
  } finally {
    uploading.value = false
  }
  return false
}

async function handleDownloadTemplate() {
  if (!idDocType.value?.id) return
  try {
    await downloadDocumentTemplate(idDocType.value.id, 'id-application-template')
    message.success('Download started.')
  } catch {
    message.error('Download failed.')
  }
}

// ======================================
// Inline Field Editor
// ======================================
function formatName(value) {
  return value.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w_]/g, '')
}

function addField() {
  localFields.value.push({
    id: uuidv4(),
    name: '',
    label: '',
    type: 'text',
    required: false,
    options: [],
    optionsText: ''
  })
}

function removeField(index) {
  localFields.value.splice(index, 1)
}

async function saveFields() {
  for (const field of localFields.value) {
    if (!field.name.trim() && field.label.trim()) field.name = formatName(field.label)
    field.name = formatName(field.name)
    if (!field.name) return message.warning('Each field must have a valid name.')
    if (!field.label.trim()) {
      field.label = field.name.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase())
    }
    if (field.type === 'select' && (!field.options || field.options.length === 0)) {
      return message.warning('Select fields must have at least one option.')
    }
  }
  saving.value = true
  try {
    const docType = await ensureIDDocType()
    await updateDocumentType(docType.id, { fields: JSON.parse(JSON.stringify(localFields.value)) })
    message.success('Fields saved.')
    await loadIDDocType()
  } catch (err) {
    console.error(err)
    message.error('Failed to save fields.')
  } finally {
    saving.value = false
  }
}

// ======================================
// Computed
// ======================================
const hasTemplate = computed(() => !!idDocType.value?.has_template)
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden animate-fade-in">

    <!-- Header -->
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="ID Template Settings" />
        <p class="text-sm text-gray-500 mt-1">
          Upload and configure the Barangay ID card template and its form fields.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <NTag :type="hasTemplate ? 'success' : 'warning'" :bordered="false" round>
          {{ hasTemplate ? 'Template Uploaded' : 'No Template' }}
        </NTag>
        <NButton v-if="hasTemplate" size="small" @click="handleDownloadTemplate">
          <template #icon><DocumentTextIcon class="w-4 h-4" /></template>
          Download
        </NButton>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p class="text-gray-500 font-medium">Loading...</p>
    </div>

    <template v-else>
      <div class="flex-1 overflow-y-auto">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">

          <!-- Left: Upload + Placeholder reference -->
          <div class="flex flex-col gap-6">

            <!-- Upload -->
            <div class="border border-gray-200 rounded-lg p-5">
              <h2 class="text-sm font-semibold text-gray-700 mb-1">Template File</h2>
              <p class="text-xs text-gray-500 mb-4 leading-relaxed">
                Upload a <strong>.docx</strong> file using
                <code class="bg-gray-100 px-1 rounded">&#123;&#123;placeholder&#125;&#125;</code>
                syntax.
              </p>
              <NUpload :custom-request="handleFileUpload" :show-file-list="false" accept=".docx">
                <NUploadDragger>
                  <div class="flex flex-col items-center py-5 gap-2">
                    <NSpin v-if="uploading" />
                    <template v-else>
                      <CloudArrowUpIcon class="w-8 h-8 text-gray-400" />
                      <p class="text-sm font-medium text-gray-600">
                        Click or drag a <span class="text-blue-600">.docx</span> here
                      </p>
                      <p class="text-xs text-gray-400">
                        {{ hasTemplate ? 'Replaces existing template' : 'No template uploaded yet' }}
                      </p>
                    </template>
                  </div>
                </NUploadDragger>
              </NUpload>
            </div>

            <!-- Fixed placeholders -->
            <div class="border border-gray-200 rounded-lg p-5">
              <div class="flex items-start gap-2 mb-3">
                <InformationCircleIcon class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h2 class="text-sm font-semibold text-gray-700">Fixed Placeholders</h2>
                  <p class="text-xs text-gray-500 mt-0.5">Auto-filled by the system.</p>
                </div>
              </div>
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100">
                    <th class="text-left py-1.5 pr-4 font-medium text-gray-500 uppercase tracking-wide">Placeholder</th>
                    <th class="text-left py-1.5 pr-4 font-medium text-gray-500 uppercase tracking-wide">Label</th>
                    <th class="text-left py-1.5 font-medium text-gray-500 uppercase tracking-wide">Source</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="f in FIXED_FIELDS" :key="f.name" class="border-b border-gray-50 last:border-0">
                    <td class="py-1.5 pr-4">
                      <code class="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-mono" v-text="'{{' + f.name + '}}'"></code>
                    </td>
                    <td class="py-1.5 pr-4 text-gray-700">{{ f.label }}</td>
                    <td class="py-1.5 text-gray-400">{{ f.source }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>

          <!-- Right: Inline field editor -->
          <div class="border border-gray-200 rounded-lg p-5 flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-sm font-semibold text-gray-700">Form Fields</h2>
                <p class="text-xs text-gray-500 mt-0.5">Fields residents fill out when applying for an ID.</p>
              </div>
              <NButton size="small" @click="addField">
                <template #icon><PlusIcon class="w-4 h-4" /></template>
                Add Field
              </NButton>
            </div>

            <!-- Empty state -->
            <div
              v-if="localFields.length === 0"
              class="flex flex-col items-center justify-center py-10 text-gray-400 gap-2 border-2 border-dashed border-gray-200 rounded-lg"
            >
              <PlusIcon class="w-7 h-7" />
              <p class="text-sm">No fields yet.</p>
              <NButton size="small" @click="addField">Add Field</NButton>
            </div>

            <!-- Field list -->
            <div v-else class="flex flex-col gap-3 overflow-y-auto flex-1">
              <div
                v-for="(field, index) in localFields"
                :key="field.id"
                class="p-4 bg-gray-50 border border-gray-200 rounded-lg flex flex-col gap-3"
              >
                <!-- Row 1: Label + Placeholder + Type + Delete -->
                <div class="grid gap-3 items-end" style="grid-template-columns: 1fr 1fr 1fr auto;">
                  <div class="flex flex-col gap-1">
                    <label class="text-xs font-medium text-gray-500">Label</label>
                    <NInput v-model:value="field.label" placeholder="e.g. Full Name" size="small" />
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs font-medium text-gray-500">Placeholder</label>
                    <NInput v-model:value="field.name" placeholder="e.g. full_name" size="small" />
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs font-medium text-gray-500">Type</label>
                    <NSelect
                      v-model:value="field.type"
                      size="small"
                      :options="[
                        { label: 'Text', value: 'text' },
                        { label: 'Number', value: 'number' },
                        { label: 'Email', value: 'email' },
                        { label: 'Telephone', value: 'tel' },
                        { label: 'Textarea', value: 'textarea' },
                        { label: 'Date', value: 'date' },
                        { label: 'Select', value: 'select' },
                      ]"
                    />
                  </div>
                  <button
                    class="p-1.5 border border-red-300 rounded text-red-400 hover:bg-red-50 transition"
                    @click="removeField(index)"
                    type="button"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>

                <!-- Row 2: Required + options -->
                <div class="flex flex-col gap-2">
                  <NCheckbox v-model:checked="field.required" size="small">Required</NCheckbox>
                  <div v-if="field.type === 'select'">
                    <NInput
                      v-model:value="field.optionsText"
                      placeholder="Comma-separated options: A, B, C"
                      size="small"
                      @input="field.options = field.optionsText.split(',').map(o => o.trim()).filter(Boolean)"
                    />
                    <p v-if="field.options?.length" class="text-xs text-gray-400 mt-1">
                      {{ field.options.length }} option(s): {{ field.options.join(', ') }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Save -->
            <div v-if="localFields.length > 0" class="pt-3 border-t border-gray-100">
              <NButton type="primary" size="small" :loading="saving" @click="saveFields">
                Save Fields
              </NButton>
            </div>
          </div>

        </div>
      </div>
    </template>

  </div>
</template>