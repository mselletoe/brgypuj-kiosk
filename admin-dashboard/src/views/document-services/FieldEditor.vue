<script setup>
import { ref, watch } from 'vue'
import { NModal, NButton, NInput, NSelect, NCheckbox, useMessage } from 'naive-ui'
import { v4 as uuidv4 } from 'uuid'
import { TrashIcon } from '@heroicons/vue/24/outline'

// Component props
const props = defineProps({
  show: Boolean,
  fieldsData: {
    type: Array,
    default: () => []
  },
  serviceId: Number
})

// Component events
const emit = defineEmits(['close', 'saved'])

const message = useMessage()
const localShow = ref(props.show)

// Sync local show state with prop
watch(() => props.show, val => {
  localShow.value = val
})
watch(localShow, val => {
  emit('update:show', val)
})

// Local fields array for editing
const localFields = ref([])

// Watch for changes in fieldsData prop and deep clone it
watch(
  () => props.fieldsData,
  (newVal) => {
    localFields.value = JSON.parse(JSON.stringify(newVal || []))
  },
  { immediate: true }
)

function formatName(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')    // spaces → underscores
    .replace(/[^\w_]/g, '')  // remove symbols
}

// Add a new field to the list
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

// Remove a field by index
function removeField(index) {
  localFields.value.splice(index, 1)
}

// Save the configured fields
function save() {
  for (const field of localFields.value) {
    // Auto-generate a safe name from label if name is empty
    if (!field.name.trim() && field.label.trim()) {
      field.name = formatName(field.label)
    }

    // Ensure final name is properly formatted
    field.name = formatName(field.name)

    if (!field.name) {
      return message.warning('Each field must have a valid name (e.g., full_name).')
    }

    if (!field.label.trim()) {
      field.label = field.name
        .replace(/_/g, ' ')              // replace underscores with spaces
        .toLowerCase()                   // make everything lowercase
        .replace(/^\w/, c => c.toUpperCase()); // capitalize the first letter only
    }

    if (field.type === 'select' && (!field.options || field.options.length === 0)) {
      return message.warning('Select fields must have at least one option.')
    }
  }

  emit('saved', JSON.parse(JSON.stringify(localFields.value)), props.serviceId)
}
</script>

<template>
  <NModal
    v-model:show="localShow"
    title="Configure Fields"
    :mask-closable="false"
    preset="card"
    style="width: 90%; max-width: 800px; max-height: 80vh; overflow-y: auto;"
    @close="emit('close')"
  >
    <div style="min-height: 200px;">
      <!-- Empty state when no fields exist -->
      <div 
        v-if="localFields.length === 0" 
        style="text-align: center; padding: 3rem 1rem; color: #999;"
      >
        <p style="margin-bottom: 1rem; font-size: 15px;">No fields configured yet.</p>
        <NButton type="primary" @click="addField">Add Your First Field</NButton>
      </div>

      <!-- List of configured fields -->
      <div v-else style="display: flex; flex-direction: column; gap: 1rem;">
        <div
          v-for="(field, index) in localFields"
          :key="field.id"
          style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 1rem; padding: 1.25rem; background: #fafafa; border: 1px solid #e5e5e5; border-radius: 8px; align-items: start;"
        >
          <!-- Label -->
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <label style="font-size: 13px; color: #666; font-weight: 500;">Field Label</label>
            <NInput
              v-model:value="field.label"
              placeholder="e.g., Field Label"
              size="medium"
              @input="field.name = formatName(field.name)"
            />
          </div>

          <!-- Template placeholder (Label) -->
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <label style="font-size: 13px; color: #666; font-weight: 500;">Template placeholder</label>
            <NInput
              v-model:value="field.name"
              placeholder="e.g., field_name"
              size="medium"
            />
          </div>

          <!-- Type -->
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <label style="font-size: 13px; color: #666; font-weight: 500;">Type</label>
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

          <!-- Remove button -->
          <button 
            style="margin-top: 1.75rem; background: transparent; border: 1px solid #ffcdd2; border-radius: 6px; padding: 0.5rem; cursor: pointer; color: #e53935; transition: all 0.2s; display: flex; align-items: center; justify-content: center;"
            @click="removeField(index)"
            @mouseenter="e => e.target.style.background = '#ffebee'"
            @mouseleave="e => e.target.style.background = 'transparent'"
            type="button"
          >
            <TrashIcon style="width: 20px; height: 20px;" />
          </button>

          <!-- Required checkbox and options on second row -->
          <div style="grid-column: 1 / -1; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
            <NCheckbox v-model:checked="field.required" size="medium">
              Required field
            </NCheckbox>

            <!-- Options input for select type fields -->
            <div v-if="field.type === 'select'" style="display: flex; flex-direction: column; gap: 0.5rem;">
              <NInput
                v-model:value="field.optionsText"
                placeholder="Options (comma separated): Option 1, Option 2, Option 3"
                @input="field.options = field.optionsText.split(',').map(o => o.trim()).filter(o => o)"
                size="medium"
              />
              <p 
                v-if="field.options && field.options.length > 0" 
                style="font-size: 12px; color: #999; margin: 0;"
              >
                {{ field.options.length }} option(s): {{ field.options.join(', ') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal footer with action buttons -->
    <template #footer>
      <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
        <NButton 
          type="default"
          @click="addField"
          size="medium"
        >
          Add field
        </NButton>
        <NButton 
          type="primary" 
          @click="save"
          :disabled="localFields.length === 0"
          size="medium"
        >
          Save
        </NButton>
      </div>
    </template>
  </NModal>
</template>