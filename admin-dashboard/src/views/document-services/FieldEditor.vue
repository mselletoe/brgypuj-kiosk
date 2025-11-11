<script setup>
import { ref, watch } from 'vue'
import { NModal, NButton, NInput, NSelect, NCheckbox, useMessage } from 'naive-ui'
import { v4 as uuidv4 } from 'uuid'

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
    :title="localFields.length === 0 ? 'Configure Fields - No fields yet' : `Configure Fields (${localFields.length})`"
    :mask-closable="false"
    preset="card"
    style="width: 90%; max-width: 900px;"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <!-- Empty state when no fields exist -->
      <div v-if="localFields.length === 0" class="text-center py-8 text-gray-500">
        <p class="mb-4">No fields configured yet.</p>
        <NButton type="primary" @click="addField">Add Your First Field</NButton>
      </div>

      <!-- List of configured fields -->
      <div v-else class="space-y-3">
        <div
          v-for="(field, index) in localFields"
          :key="field.id"
          class="border border-gray-200 rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <!-- Field header with number and remove button -->
          <div class="flex items-center justify-between mb-3">
            <span class="font-semibold text-gray-700">Field {{ index + 1 }}</span>
            <NButton 
              type="error" 
              size="small" 
              quaternary
              @click="removeField(index)"
            >
              Remove
            </NButton>
          </div>

          <!-- Field name and type in a row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            <div>
              <label class="text-sm text-gray-600 mb-1 block">Field Name</label>
              <NInput
                v-model:value="field.name"
                placeholder="e.g., full_name, contact_number"
                size="medium"
                @input="field.name = formatName(field.name)"
              />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">Field Type</label>
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
          </div>

          <!-- Required checkbox -->
          <div class="mb-3">
            <NCheckbox v-model:checked="field.required" size="large">
              Required field
            </NCheckbox>
          </div>

          <!-- Options input for select type fields -->
          <div v-if="field.type === 'select'">
            <label class="text-sm text-gray-600 mb-1 block">Options (comma separated)</label>
            <NInput
              v-model:value="field.optionsText"
              placeholder="e.g., Option 1, Option 2, Option 3"
              @input="field.options = field.optionsText.split(',').map(o => o.trim()).filter(o => o)"
              size="medium"
            />
            <!-- Show parsed options preview -->
            <p v-if="field.options && field.options.length > 0" class="text-xs text-gray-500 mt-1">
              {{ field.options.length }} option(s): {{ field.options.join(', ') }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal footer with action buttons -->
    <template #footer>
      <div class="flex justify-between items-center">
        <NButton 
          type="default" 
          @click="addField"
          size="medium"
        >
          + Add Field
        </NButton>
        <div class="flex gap-2">
          <NButton 
            @click="localShow = false; emit('close')"
            size="medium"
          >
            Cancel
          </NButton>
          <NButton 
            type="primary" 
            @click="save"
            :disabled="localFields.length === 0"
            size="medium"
          >
            Save Configuration
          </NButton>
        </div>
      </div>
    </template>
  </NModal>
</template>

<style scoped>
.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}
</style>