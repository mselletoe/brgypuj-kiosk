<script setup>
import { ref, watch } from 'vue'
import { NModal, NButton, NInput, NSelect, NCheckbox, useMessage } from 'naive-ui'
import { v4 as uuidv4 } from 'uuid'

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
const localShow = ref(props.show)

watch(() => props.show, val => {
  localShow.value = val
})
watch(localShow, val => {
  emit('update:show', val)
})

const localFields = ref([])

watch(
  () => props.fieldsData,
  (newVal) => {
    localFields.value = JSON.parse(JSON.stringify(newVal || []))
  },
  { immediate: true }
)

// Add new field
function addField() {
  localFields.value.push({
    id: uuidv4(),
    name: '',
    label: '',
    type: 'text',
    required: false,
    options: []
  })
}

// Remove field
function removeField(index) {
  localFields.value.splice(index, 1)
}

// Handle saving fields
function save() {
  // Validation: names and labels required
  for (const field of localFields.value) {
    if (!field.name.trim() || !field.label.trim()) {
      return message.warning('All fields must have a name and label.')
    }
    if (field.type === 'select' && (!field.options || field.options.length === 0)) {
      return message.warning('Select fields must have at least one option.')
    }
  }

  emit('saved', JSON.parse(JSON.stringify(localFields.value)), props.serviceId)
}
</script>

<template>
    <div>
        <NModal
            v-model:show="localShow"
            title="Configure Fields"
            closable
            :mask-closable="false"
            @close="localShow = false; emit('close')"
            style="max-width: 800px;"
            class="bg-white p-4 rounded-md shadow-md space-y-4"
        >
            <div class="space-y-4">
            <div
                v-for="(field, index) in localFields"
                :key="field.id"
                class="border p-4 rounded-md flex flex-col gap-2"
            >
                <div class="flex gap-2">
                <NInput
                    v-model:value="field.name"
                    placeholder="Field Name (unique identifier)"
                    style="flex: 1"
                />
                <NInput
                    v-model:value="field.label"
                    placeholder="Label (what user sees)"
                    style="flex: 1"
                />
                </div>

                <div class="flex items-center gap-2">
                <NSelect
                    v-model:value="field.type"
                    :options="[
                    { label: 'Text', value: 'text' },
                    { label: 'Number', value: 'number' },
                    { label: 'Email', value: 'email' },
                    { label: 'Telephone', value: 'tel' },
                    { label: 'Textarea', value: 'textarea' },
                    { label: 'Date', value: 'date' },
                    { label: 'Select', value: 'select' }
                    ]"
                    placeholder="Field Type"
                />
                <NCheckbox v-model:value="field.required">Required</NCheckbox>
                <NButton type="error" size="small" @click="removeField(index)">Remove</NButton>
                </div>

                <!-- Options for select fields -->
                <div v-if="field.type === 'select'" class="flex gap-2">
                <NInput
                    v-model:value="field.optionsText"
                    placeholder="Options (comma separated)"
                    @input="field.options = field.optionsText.split(',').map(o => o.trim()).filter(o => o)"
                    style="flex: 1"
                />
                </div>
            </div>

            <div class="flex justify-between mt-4">
                <NButton type="default" @click="addField">Add Field</NButton>
                <NButton type="primary" @click="save">Save Fields</NButton>
            </div>
            </div>
        </NModal>        
    </div>
</template>