<script setup>
/**
 * @file views/document-services/FieldEditor.vue
 * @description Modal component for configuring dynamic form fields on a document type.
 * Each field defines a label, template placeholder name, input type, and whether
 * it is required. Select fields also support a comma-separated options list.
 */

import { ref, watch } from 'vue'
import { NModal, NButton, NInput, NSelect, NCheckbox, useMessage } from 'naive-ui'
import { v4 as uuidv4 } from 'uuid'
import { TrashIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  show: Boolean,
  fieldsData: {
    type: Array,
    default: () => []
  },
  serviceId: Number
})

const emit = defineEmits(['close', 'saved'])
const message = useMessage()
const localFields = ref([])

watch(
  () => props.fieldsData,
  (newVal) => {
    localFields.value = JSON.parse(JSON.stringify(newVal || []))
  },
  { immediate: true }
)

// =============================================================================
// FIELD HELPERS
// =============================================================================
function formatName(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^\w_]/g, '')
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

// =============================================================================
// SAVE
// =============================================================================
function save() {
  for (const field of localFields.value) {
    if (!field.name.trim() && field.label.trim()) {
      field.name = formatName(field.label)
    }

    field.name = formatName(field.name)

    if (!field.name) {
      return message.warning('Each field must have a valid name (e.g., full_name).')
    }

    if (!field.label.trim()) {
      field.label = field.name
        .replace(/_/g, ' ')
        .toLowerCase()
        .replace(/^\w/, c => c.toUpperCase())
    }

    if (field.type === 'select' && (!field.options || field.options.length === 0)) {
      return message.warning('Select fields must have at least one option.')
    }
  }

  emit('saved', JSON.parse(JSON.stringify(localFields.value)), props.serviceId)
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <NModal :show="show" @update:show="handleClose" :mask-closable="false">
    <div class="w-[800px] max-h-[80vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col">

      <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
        <div>
          <h2 class="text-base font-semibold text-gray-800">Configure Fields</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            Define the input fields residents will fill out when requesting this document.
          </p>
        </div>
        <button @click="handleClose" class="p-1 rounded hover:bg-gray-200 transition">
          <XMarkIcon class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div class="px-6 py-4 overflow-y-auto flex-1">

        <div
          v-if="localFields.length === 0"
          class="flex flex-col items-center justify-center py-12 text-gray-400 gap-3"
        >
          <p class="text-sm">No fields configured yet.</p>
          <NButton type="primary" @click="addField">Add Your First Field</NButton>
        </div>

        <div v-else class="flex flex-col gap-4">
          <div
            v-for="(field, index) in localFields"
            :key="field.id"
            class="grid gap-4 p-5 bg-gray-50 border border-gray-200 rounded-lg items-start"
            style="grid-template-columns: 1fr 1fr 1fr auto;"
          >
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-gray-500">Field Label</label>
              <NInput
                v-model:value="field.label"
                placeholder="e.g., Field Label"
                size="medium"
                @input="field.name = formatName(field.name)"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-gray-500">Template Placeholder</label>
              <NInput
                v-model:value="field.name"
                placeholder="e.g., field_name"
                size="medium"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-gray-500">Type</label>
              <NSelect
                v-model:value="field.type"
                :options="[
                  { label: 'Text', value: 'text' },
                  { label: 'Number', value: 'number' },
                  { label: 'Email', value: 'email' },
                  { label: 'Telephone', value: 'tel' },
                  { label: 'Textarea', value: 'textarea' },
                  { label: 'Date', value: 'date' },
                  { label: 'Select Dropdown', value: 'select' }
                ]"
                size="medium"
              />
            </div>

            <button
              class="mt-6 p-2 border border-red-400 rounded-lg text-red-500 hover:bg-red-50 transition flex items-center justify-center"
              @click="removeField(index)"
              type="button"
            >
              <TrashIcon class="w-5 h-5" />
            </button>

            <div class="col-span-full flex flex-col gap-3">
              <NCheckbox v-model:checked="field.required" size="medium">
                Required field
              </NCheckbox>

              <div v-if="field.type === 'select'" class="flex flex-col gap-1.5">
                <NInput
                  v-model:value="field.optionsText"
                  placeholder="Options (comma separated): Option 1, Option 2, Option 3"
                  @input="field.options = field.optionsText.split(',').map(o => o.trim()).filter(o => o)"
                  size="medium"
                />
                <p v-if="field.options && field.options.length > 0" class="text-xs text-gray-400">
                  {{ field.options.length }} option(s): {{ field.options.join(', ') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between px-6 py-4 border-t">
        <NButton @click="addField" size="medium">
          Add Field
        </NButton>
        <div class="flex gap-3">
          <NButton @click="handleClose">Cancel</NButton>
          <NButton
            type="primary"
            @click="save"
            :disabled="localFields.length === 0"
          >
            Save Fields
          </NButton>
        </div>
      </div>

    </div>
  </NModal>
</template>