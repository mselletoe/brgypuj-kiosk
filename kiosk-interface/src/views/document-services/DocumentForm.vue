<script setup>
/**
 * @file DocumentForm.vue
 * @description Dynamic Form Renderer for Document Requests.
 * This component builds a form based on administrative configuration, 
 * automatically maps and pre-fills resident data for authenticated RFID users, 
 * and handles localized field validation.
 */
import { ref, watch } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { CalendarIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import { LockClosedIcon } from '@heroicons/vue/24/solid'

// --- Props Configuration ---
const props = defineProps({
  config: Object,
  initialData: {
    type: Object,
    default: () => ({})
  },
  residentData: {
    type: Object,
    default: () => null
  },
  isRfidUser: {
    type: Boolean,
    default: false
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['continue'])

// --- Form & Error States ---
const formData = ref({})
const errors = ref({})

/**
 * Field Mapping Dictionary
 * Maps standardized database keys (keys) to various potential form field 
 * naming conventions (values) set by the admin in the dashboard.
 */
const fieldMapping = {
  // Name fields
  full_name: ['full_name', 'name', 'resident_name', 'applicant_name'],
  first_name: ['first_name', 'fname'],
  middle_name: ['middle_name', 'mname'],
  last_name: ['last_name', 'lname', 'surname'],
  suffix: ['suffix', 'name_suffix'],
  
  // Personal info
  gender: ['gender', 'sex'],
  birthdate: ['birthdate', 'date_of_birth', 'birth_date', 'dob'],
  age: ['age'],
  
  // Contact info
  email: ['email', 'email_address'],
  phone_number: ['phone_number', 'contact_number', 'mobile_number', 'phone', 'contact'],
  
  // Address fields
  unit_blk_street: ['unit_blk_street', 'street', 'house_number', 'house_no'],
  purok_name: ['purok_name', 'purok', 'sitio'],
  barangay: ['barangay', 'brgy'],
  municipality: ['municipality', 'city'],
  province: ['province', 'prov'],
  region: ['region'],
  full_address: ['full_address', 'address', 'complete_address'],
  
  // Residency info
  years_residency: ['yr_res', 'years_residency', 'years_of_residency', 'residency_years', 'year_residency'],
  residency_start_date: ['residency_start_date', 'date_started_residency'],
  
  // RFID info
  rfid_uid: ['rfid_uid', 'rfid', 'card_number', 'rfid_number'],
}

// Tracks fields that were automatically populated from the resident profile
const preFilledFields = ref(new Set())

/**
 * Initializes form values. 
 * Combines initial state with profile-based autofill logic.
 */
const initializeFormData = () => {
  props.config.fields.forEach((field) => {
    let value = props.initialData[field.name] || ''
    let isPrefilled = false

    // Attempt to autofill if user is authenticated and resident data is available
    if (props.isRfidUser && props.residentData) {
      // Look through all possible mappings for this field
      for (const [residentField, formFieldVariants] of Object.entries(fieldMapping)) {
        if (formFieldVariants.includes(field.name)) {
          const residentValue = props.residentData[residentField]
          
          if (residentValue !== null && residentValue !== undefined && residentValue !== '') {
            value = residentValue
            isPrefilled = true
            preFilledFields.value.add(field.name)
            break
          }
        }
      }
    }

    formData.value[field.name] = value
    errors.value[field.name] = ''
  })
}

initializeFormData()

/**
 * Watcher: Resident Data Sync
 * Reacts to async resident data loading. Populates empty fields if data 
 * arrives after the component has already mounted.
 */
watch(() => props.residentData, (newData) => {
  if (!newData || !props.isRfidUser) return
  
  props.config.fields.forEach((field) => {
    // Only autofill if field is currently empty
    if (formData.value[field.name]) return
    
    for (const [residentField, formFieldVariants] of Object.entries(fieldMapping)) {
      if (formFieldVariants.includes(field.name)) {
        const residentValue = newData[residentField]
        
        if (residentValue !== null && residentValue !== undefined && residentValue !== '') {
          formData.value[field.name] = residentValue
          preFilledFields.value.add(field.name)
          break
        }
      }
    }
  })
}, { immediate: true, deep: true })

// ==============================================
// Helpers
// ==============================================

/**
 * Identifies if a field is locked based on RFID authentication.
 */
const isPreFilled = (fieldName) => {
  return props.isRfidUser && preFilledFields.value.has(fieldName)
}

/**
 * Dynamically adjusts placeholders based on field status.
 */
const formatPlaceholder = (placeholder, label, isPrefilled) => {
  if (isPrefilled) {
    return 'Auto-filled from your profile'
  }
  return placeholder || `Enter ${label.toLowerCase()}`
}

/**
 * Validates required fields before allowing submission.
 * @returns {boolean} True if all required fields are populated.
 */
const validate = () => {
  let isValid = true
  props.config.fields.forEach((field) => {
    errors.value[field.name] = ''
    
    const value = formData.value[field.name]
    const isEmpty = value === null || value === undefined || value === ''
    
    if (field.required && isEmpty) {
      errors.value[field.name] = 'This field is required'
      isValid = false
    }
  })
  return isValid
}

/**
 * Emits the 'continue' event with valid form data to the parent wrapper.
 */
const handleContinue = () => {
  if (props.isSubmitting) return
  if (validate()) {
    emit('continue', formData.value)
  }
}

// Tracks which custom select dropdown is currently open
const openDropdown = ref(null)

const toggleSelectDropdown = (fieldName) => {
  openDropdown.value = openDropdown.value === fieldName ? null : fieldName
}

const selectOption = (fieldName, option) => {
  formData.value[fieldName] = option
  openDropdown.value = null
  errors.value[fieldName] = ''
}

defineExpose({
  handleContinue
})
</script>

<template>
  <div class="space-y-5">

    <!-- Autofill Notice -->
    <!-- <div v-if="isRfidUser && residentData" class="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
      <LockClosedIcon class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
      <div>
        <p class="text-sm text-blue-800 font-semibold">Your information has been pre-filled</p>
        <p class="text-xs text-blue-600 mt-1">Fields with a lock icon are pulled from your resident profile and cannot be edited here.</p>
      </div>
    </div> -->

    <!-- Form Fields Grid -->
    <div class="grid grid-cols-1 md:grid-cols gap-5">
      <div v-for="field in config.fields" :key="field.id || field.name" class="flex flex-col">
        <label class="flex items-center gap-2 mb-2 font-bold text-[#003A6B]">
          {{ field.label }}
          <span v-if="field.required" class="text-red-500">*</span>
          <LockClosedIcon 
            v-if="isPreFilled(field.name)" 
            class="w-4 h-4 text-blue-600" 
            title="Auto-filled from your profile"
          />
        </label>

        <!-- Text / Email / Number / Tel -->
        <input
          v-if="['text','email','tel','number'].includes(field.type)"
          v-model="formData[field.name]"
          :type="field.type"
          :placeholder="formatPlaceholder(field.placeholder, field.label, isPreFilled(field.name))"
          :readonly="isPreFilled(field.name) || props.isSubmitting"
          :disabled="isPreFilled(field.name) || props.isSubmitting"
          :class="[
            errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-gray-300',
            isPreFilled(field.name) ? 'bg-gray-100 cursor-not-allowed text-gray-700' : 'bg-white',
            'w-full h-[48px] px-4 py-3 border rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]'
          ]"
        />

        <!-- Date picker -->
        <VueDatePicker
          v-else-if="field.type === 'date'"
          v-model="formData[field.name]"
          :enable-time-picker="false"
          :disabled="isPreFilled(field.name) || props.isSubmitting"
          auto-apply
          teleport-center
          format="MM/dd/yyyy"
          :max-date="new Date()"
          :placeholder="formatPlaceholder(field.placeholder, field.label, isPreFilled(field.name))"
          :input-class-name="[
            'w-full h-[48px] pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]',
            isPreFilled(field.name) ? 'bg-gray-100 cursor-not-allowed' : ''
          ].join(' ')"
        >
          <template #input-icon>
            <LockClosedIcon v-if="isPreFilled(field.name)" class="w-5 h-5 text-blue-600 ml-3"/>
            <CalendarIcon v-else class="w-5 h-5 text-gray-400 ml-3"/>
          </template>
        </VueDatePicker>

        <!-- Textarea -->
        <textarea
          v-else-if="field.type === 'textarea'"
          v-model="formData[field.name]"
          :placeholder="formatPlaceholder(field.placeholder, field.label, isPreFilled(field.name))"
          :readonly="isPreFilled(field.name) || props.isSubmitting"
          :disabled="isPreFilled(field.name) || props.isSubmitting"
          :class="[
            errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-gray-300',
            isPreFilled(field.name) ? 'bg-gray-100 cursor-not-allowed text-gray-700' : 'bg-white',
            'w-full px-4 py-3 border rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]'
          ]"
        ></textarea>

        <!-- Select -->
        <div
          v-else-if="field.type === 'select'"
          class="relative"
        >
          <button
            type="button"
            @click="!isPreFilled(field.name) && !props.isSubmitting && toggleSelectDropdown(field.name)"
            :disabled="isPreFilled(field.name) || props.isSubmitting"
            :class="[
              errors[field.name] ? 'border-red-500' : 'border-gray-300',
              isPreFilled(field.name) ? 'bg-gray-100 cursor-not-allowed' : 'bg-white',
              'w-full h-[48px] px-4 py-3 border rounded-xl shadow-sm transition-shadow flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-[#013C6D]'
            ]"
          >
            <span :class="formData[field.name] ? 'text-[#03335C] font-bold' : 'text-gray-400'">
              {{ formData[field.name] || `Select ${field.label}` }}
            </span>
            <LockClosedIcon v-if="isPreFilled(field.name)" class="w-4 h-4 text-blue-600" />
            <ChevronDownIcon v-else class="w-5 h-5 text-[#03335C]" />
          </button>
          <div
            v-if="openDropdown === field.name"
            class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-48 overflow-y-auto custom-scroll"
          >
            <button
              v-for="option in (Array.isArray(field.options) ? field.options : [])"
              :key="option"
              type="button"
              @click="selectOption(field.name, option)"
              class="w-full text-left py-2.5 px-4 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm border-b border-gray-50 last:border-0"
            >
              {{ option }}
            </button>
          </div>
        </div>

        <!-- Error message -->
        <p v-if="errors[field.name]" class="text-red-500 text-xs mt-1 italic">
          {{ errors[field.name] }}
        </p>
      </div>
    </div>
  </div>
</template>