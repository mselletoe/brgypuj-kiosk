<script setup>
import { ref } from 'vue'

const props = defineProps({
  config: Object,
  initialData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['continue'])

// Initialize form data
const formData = ref({})
props.config.fields.forEach(field => {
  formData.value[field.name] = props.initialData[field.name] || ''
})

const validate = () => {
  for (const field of props.config.fields) {
    if (field.required && !formData.value[field.name]) {
      alert(`Please fill in: ${field.label}`)
      return false
    }
  }
  return true
}

const handleContinue = () => {
  if (validate()) {
    emit('continue', formData.value)
  }
}
</script>

<template>
  <div class="space-y-5">
    <!-- Dynamically render fields based on config -->
    <div v-for="field in config.fields" :key="field.name">
      <label class="block mb-2 font-medium text-gray-700">
        {{ field.label }}
        <span v-if="field.required" class="text-red-500">*</span>
      </label>

      <!-- Text Input -->
      <input 
        v-if="field.type === 'text' || field.type === 'email' || field.type === 'tel'"
        v-model="formData[field.name]"
        :type="field.type"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        :placeholder="field.placeholder || field.label"
      />

      <!-- Number Input -->
      <input 
        v-else-if="field.type === 'number'"
        v-model.number="formData[field.name]"
        type="number"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        :placeholder="field.placeholder || field.label"
      />

      <!-- Date Input -->
      <input 
        v-else-if="field.type === 'date'"
        v-model="formData[field.name]"
        type="date"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />

      <!-- Textarea -->
      <textarea 
        v-else-if="field.type === 'textarea'"
        v-model="formData[field.name]"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        rows="3"
        :placeholder="field.placeholder || field.label"
      ></textarea>

      <!-- Select -->
      <select 
        v-else-if="field.type === 'select'"
        v-model="formData[field.name]"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Select {{ field.label }}</option>
        <option v-for="option in field.options" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <button
      @click="handleContinue"
      class="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold mt-6 transition"
    >
      Continue to Preview
    </button>
  </div>
</template>