<script setup>
/**
 * @file views/document-services/DocumentForm.vue
 * @description Renders a dynamic form based on a document type's configured field definitions.
 * Supports text, email, tel, number, textarea, date, and select field types.
 * For authenticated RFID users, known fields are auto-filled and locked from editing
 * using a field mapping that matches resident profile data to form field names.
 */

import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { CalendarIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import { LockClosedIcon } from '@heroicons/vue/24/solid'
import Keyboard from '@/components/shared/Keyboard.vue'

const props = defineProps({
  config: Object,

  /** Pre-existing form values to restore (e.g. when navigating back) */
  initialData: {
    type: Object,
    default: () => ({})
  },

  /** Authenticated resident's profile data used for auto-fill */
  residentData: {
    type: Object,
    default: () => null
  },

  /** When true, enables auto-fill from residentData and locks matched fields */
  isRfidUser: {
    type: Boolean,
    default: false
  },

  /** Disables all inputs while the form submission is in progress */
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['continue'])
const { t } = useI18n()

const formData = ref({})
const errors = ref({})

// =============================================================================
// FIELD MAPPING - PLACEHOLDERS
// =============================================================================
const fieldMapping = {
  full_name: ['full_name', 'name', 'resident_name', 'applicant_name'],
  first_name: ['first_name', 'fname'],
  middle_name: ['middle_name', 'mname'],
  last_name: ['last_name', 'lname', 'surname'],
  suffix: ['suffix', 'name_suffix'],
  
  gender: ['gender', 'sex'],
  birthdate: ['birthdate', 'date_of_birth', 'birth_date', 'dob'],
  age: ['age'],
  
  email: ['email', 'email_address'],
  phone_number: ['phone_number', 'contact_number', 'mobile_number', 'phone', 'contact'],
  
  unit_blk_street: ['unit_blk_street', 'street', 'house_number', 'house_no'],
  purok_name: ['purok_name', 'purok', 'sitio'],
  barangay: ['barangay', 'brgy'],
  municipality: ['municipality', 'city'],
  province: ['province', 'prov'],
  region: ['region'],
  full_address: ['full_address', 'address', 'complete_address'],
  
  years_residency: ['yr_res', 'years_residency', 'years_of_residency', 'residency_years', 'year_residency'],
  residency_start_date: ['rds', 'residency_start_date', 'date_started_residency'],
  
  rfid_uid: ['rfid_uid', 'rfid', 'card_number', 'rfid_number'],
}

// =============================================================================
// FORM INITIALIZATION
// =============================================================================
const preFilledFields = ref(new Set())

const initializeFormData = () => {
  props.config.fields.forEach((field) => {
    let value = props.initialData[field.name] || ''
    let isPrefilled = false

    if (props.isRfidUser && props.residentData) {
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

watch(() => props.residentData, (newData) => {
  if (!newData || !props.isRfidUser) return
  
  props.config.fields.forEach((field) => {
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


// =============================================================================
// FIELD HELPERS
// =============================================================================

const isPreFilled = (fieldName) => {
  return props.isRfidUser && preFilledFields.value.has(fieldName)
}

const formatPlaceholder = (placeholder, label, isPrefilled) => {
  if (isPrefilled) {
    return t('autoFilledProfile')
  }
  return placeholder || `Enter ${label.toLowerCase()}`
}


// =============================================================================
// VALIDATION
// =============================================================================
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

const handleContinue = () => {
  if (props.isSubmitting) return
  if (validate()) {
    emit('continue', formData.value)
  }
}

defineExpose({
  handleContinue
})

// =============================================================================
// SELECT DROPDOWN
// =============================================================================
const openDropdown = ref(null)

const toggleSelectDropdown = (fieldName) => {
  openDropdown.value = openDropdown.value === fieldName ? null : fieldName
}

const selectOption = (fieldName, option) => {
  formData.value[fieldName] = option
  openDropdown.value = null
  errors.value[fieldName] = ''
}

// =============================================================================
// ON-SCREEN KEYBOARD
// =============================================================================
const showKeyboard = ref(false)
const activeFieldName = ref(null)
const activeFieldType = ref(null) // 'input' | 'textarea'

const openKeyboard = (fieldName, fieldType, elementId) => {
  openDropdown.value = null
  activeFieldName.value = fieldName
  activeFieldType.value = fieldType
  showKeyboard.value = true

  nextTick(() => {
    const el = elementId ? document.getElementById(elementId) : null
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

const hideKeyboard = () => {
  showKeyboard.value = false
  activeFieldName.value = null
  activeFieldType.value = null
}

const handleKeyPress = (char) => {
  if (!activeFieldName.value) return
  const current = formData.value[activeFieldName.value] ?? ''
  formData.value[activeFieldName.value] = current + char
  errors.value[activeFieldName.value] = ''
}

const handleDelete = () => {
  if (!activeFieldName.value) return
  const current = String(formData.value[activeFieldName.value] ?? '')
  formData.value[activeFieldName.value] = current.slice(0, -1)
}

const handleEnter = () => {
  if (activeFieldType.value === 'textarea') {
    const current = formData.value[activeFieldName.value] ?? ''
    formData.value[activeFieldName.value] = current + '\n'
  } else {
    hideKeyboard()
  }
}

const handleTab = () => {
  hideKeyboard()
}
</script>

<template>
  <div class="space-y-5" :class="{ 'content-with-keyboard': showKeyboard }">

    <div class="grid grid-cols-1 md:grid-cols gap-5">
      <div v-for="field in config.fields" :key="field.id || field.name" class="flex flex-col">
        <label class="flex items-center gap-2 mb-2 font-bold text-[#003A6B]">
          {{ field.label }}
          <span v-if="field.required" class="text-red-500">*</span>
          <LockClosedIcon 
            v-if="isPreFilled(field.name)" 
            class="w-4 h-4 text-blue-600" 
            :title="t('autoFilledProfile')"
          />
        </label>

        <input
          v-if="['text','email','tel','number'].includes(field.type)"
          :id="`field-${field.name}`"
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
          @focus="!isPreFilled(field.name) && !isSubmitting && openKeyboard(field.name, 'input', `field-${field.name}`)"
        />

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
          :ui="{ input: ['dp-field', isPreFilled(field.name) ? 'dp-field--prefilled' : ''] }"
        >
          <template #input-icon>
            <LockClosedIcon v-if="isPreFilled(field.name)" class="w-5 h-5 text-blue-600 ml-3"/>
            <CalendarIcon v-else class="w-5 h-5 text-gray-400 ml-3"/>
          </template>
        </VueDatePicker>

        <textarea
          v-else-if="field.type === 'textarea'"
          :id="`field-${field.name}`"
          v-model="formData[field.name]"
          :placeholder="formatPlaceholder(field.placeholder, field.label, isPreFilled(field.name))"
          :readonly="isPreFilled(field.name) || props.isSubmitting"
          :disabled="isPreFilled(field.name) || props.isSubmitting"
          :class="[
            errors[field.name] ? 'border-red-500 focus:ring-red-500' : 'border-gray-300',
            isPreFilled(field.name) ? 'bg-gray-100 cursor-not-allowed text-gray-700' : 'bg-white',
            'w-full px-4 py-3 border rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]'
          ]"
          @focus="!isPreFilled(field.name) && !isSubmitting && openKeyboard(field.name, 'textarea', `field-${field.name}`)"
        ></textarea>

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
              {{ formData[field.name] || `${t('select')} ${field.label}` }}
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

        <p v-if="errors[field.name]" class="text-red-500 text-xs mt-1 italic">
          {{ errors[field.name] }}
        </p>
      </div>
    </div>
  </div>

  <Transition name="slide-up">
    <Keyboard
      v-if="showKeyboard"
      @key-press="handleKeyPress"
      @delete="handleDelete"
      @enter="handleEnter"
      @tab="handleTab"
      @hide-keyboard="hideKeyboard"
      :active-input-type="activeFieldType === 'textarea' ? 'textarea' : 'text'"
    />
  </Transition>
</template>

<style scoped>
.content-with-keyboard {
  padding-bottom: 210px;
  transition: padding-bottom 0.3s ease-out;
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>

<style>
.dp-field.dp__input {
  height: 48px !important;
  border-radius: 0.75rem !important;
  border-color: #d1d5db !important;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
  padding-top: 0.75rem !important;
  padding-bottom: 0.75rem !important;
  font-size: 1rem !important;
}

.dp-field.dp__input:focus {
  border-color: #013C6D !important;
  box-shadow: 0 0 0 2px #013C6D !important;
}

.dp-field--prefilled.dp__input {
  background-color: #f3f4f6 !important;
  color: #374151 !important;
  cursor: not-allowed !important;
}

.dp__input_wrap {
  border: none !important;
  box-shadow: none !important;
}
</style>