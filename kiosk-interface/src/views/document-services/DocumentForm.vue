<script setup>
import { ref } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { CalendarIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  config: Object,
  initialData: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['continue'])

// ==============================================
// Initialize form data and errors
// ==============================================
const formData = ref({})
const errors = ref({})

props.config.fields.forEach((field) => {
  formData.value[field.name] = props.initialData[field.name] || ''
  errors.value[field.name] = '' // initialize error message
})

// ==============================================
// Helper function to format placeholder text
// ==============================================
const formatPlaceholder = (placeholder, label) => `e.g. "${placeholder || label}"`

// ==============================================
// Validation
// ==============================================
const validate = () => {
  let isValid = true
  props.config.fields.forEach((field) => {
    errors.value[field.name] = ''
    if (field.required && !formData.value[field.name]) {
      errors.value[field.name] = 'This field is required'
      isValid = false
    }
  })
  return isValid
}

const handleContinue = () => {
  if (validate()) {
    emit('continue', formData.value)
  }
}
</script>

<template>
  <div class="space-y-5">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div v-for="field in config.fields" :key="field.name" class="flex flex-col">
        <label class="block mb-2 font-bold text-[#003A6B]">
          {{ field.label }} <span v-if="field.required" class="text-red-500">*</span>
        </label>

        <!-- Text / Email / Tel / Number -->
        <input
          v-if="['text', 'email', 'tel', 'number'].includes(field.type)"
          v-model="formData[field.name]"
          :type="field.type"
          :placeholder="formatPlaceholder(field.placeholder, field.label)"
          :maxlength="field.type === 'tel' ? 11 : null"
          inputmode="numeric"
          pattern="[0-9]*"
          @input="(e) => {
            if (field.type === 'tel') {
              e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 11)
              formData[field.name] = e.target.value
            }
          }"
          :class="[errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-[#464646] focus:ring-blue-500', 'w-full p-3 border rounded-lg shadow-md transition-shadow duration-200 focus:shadow-lg focus:ring-2']"
        />

        <!-- Date Picker -->
        <VueDatePicker
          v-else-if="field.type === 'date'"
          v-model="formData[field.name]"
          :enable-time-picker="false"
          auto-apply
          teleport-center
          format="MM/dd/yyyy"
          :max-date="new Date()"
          :placeholder="formatPlaceholder(field.placeholder, field.label)"
          input-class-name="'w-full p-3 border rounded-lg shadow-md transition-shadow duration-200 focus:shadow-lg focus:ring-2'"
        >
          <template #input-icon>
            <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
          </template>
        </VueDatePicker>

        <!-- Textarea -->
        <textarea
          v-else-if="field.type === 'textarea'"
          v-model="formData[field.name]"
          :placeholder="formatPlaceholder(field.placeholder, field.label)"
          :class="[errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-[#464646] focus:ring-blue-500', 'w-full h-[48px] p-3 border rounded-lg shadow-md transition-shadow duration-200 focus:shadow-lg focus:ring-2 leading-tight resize-none placeholder:italic']"
        ></textarea>

        <!-- Select -->
        <select
          v-else-if="field.type === 'select'"
          v-model="formData[field.name]"
          :class="[errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-[#464646] focus:ring-blue-500', 'w-full p-3 border rounded-lg shadow-md transition-shadow duration-200 focus:shadow-lg focus:ring-2']"
        >
          <option value="">Select {{ field.label }}</option>
          <option v-for="option in (Array.isArray(field.options) ? field.options : [])" :key="option" :value="option">
            {{ option }}
          </option>
        </select>

        <!-- Error message -->
        <p v-if="errors[field.name]" class="text-red-500 text-[10px] text-sm mt-1 italic">{{ errors[field.name] }}</p>
      </div>
    </div>

    <div class="flex justify-end">
      <button
        @click="handleContinue"
        class="px-8 py-3 bg-[#003A6B] text-white font-semibold rounded-full hover:bg-[#001F40] transition"
      >
        Next
      </button>
    </div>
  </div>
</template>