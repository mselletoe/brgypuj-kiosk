<script setup>
import { ref, computed } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import PrimaryButton from '@/components/shared/PrimaryButton.vue'
import { DocumentTextIcon } from '@heroicons/vue/24/outline'

// --- Props & Emits ---
const props = defineProps({
  borrowerInfo: Object,
  goNext: Function,
  goBack: Function,
})
const emit = defineEmits(['update:borrower-info'])

// --- Local State ---

// Create a local ref to bind to the form using v-model
// Initialize it with data from the prop, if it exists
const localInfo = ref({
  contactPerson: props.borrowerInfo.contactPerson || '',
  contactNumber: props.borrowerInfo.contactNumber || '',
  purpose: props.borrowerInfo.purpose || null,
  notes: props.borrowerInfo.notes || ''
})

// Options for the dropdown
const purposeOptions = ref([
  'Barangay Event',
  'Personal Event (Birthday, Wedding, etc.)',
  'Community Meeting',
  'Emergency Use',
  'Other'
])

// --- Computed Properties ---

// Check if all required fields are filled
const isFormValid = computed(() => {
  return localInfo.value.contactPerson &&
         localInfo.value.contactNumber &&
         localInfo.value.purpose
})

// --- Methods ---
const handleBack = () => {
  props.goBack('dates') // Go back to the 'dates' step
}

const handleNext = () => {
  // 1. Emit the local form data up to the parent
  emit('update:borrower-info', localInfo.value)
  
  // 2. Go to the next step
  props.goNext('review')
}

// Re-usable class for form inputs
const inputClass = "w-full px-4 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D]"
</script>

<template>
  <div class="py-0 p-8">
    
    <div class="flex items-center gap-4">
      <ArrowBackButton @click="handleBack" />
      <h1 class="text-[40px] font-bold text-[#013C6D]">Equipment Borrowing</h1>
    </div>

    <div class="mt-6 bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      
      <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
        <DocumentTextIcon class="w-8 h-8" />
        Borrowing Information
      </h3>

      <div class="mt-6 grid grid-cols-2 gap-x-6 gap-y-4">
        
        <div>
          <label for="contact-person" class="block text-base font-medium text-gray-700 mb-1">
            Contact Person *
          </label>
          <input 
            id="contact-person"
            v-model="localInfo.contactPerson"
            type="text" 
            placeholder="Name" 
            :class="inputClass" 
          />
        </div>

        <div>
          <label for="contact-number" class="block text-base font-medium text-gray-700 mb-1">
            Contact Number *
          </label>
          <input 
            id="contact-number"
            v-model="localInfo.contactNumber"
            type="tel" 
            placeholder="Phone Number" 
            :class="inputClass" 
          />
        </div>

        <div>
          <label for="purpose" class="block text-base font-medium text-gray-700 mb-1">
            Purpose of Borrowing *
          </label>
          <select 
            id="purpose"
            v-model="localInfo.purpose" 
            :class="[inputClass, { 'text-gray-500': !localInfo.purpose }]"
          >
            <option :value="null" disabled>Select</option>
            <option v-for="option in purposeOptions" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
        </div>

        <div>
          <label for="notes" class="block text-base font-medium text-gray-700 mb-1">
            Additional Notes (Optional)
          </label>
          <textarea 
            id="notes"
            v-model="localInfo.notes"
            rows="3"
            placeholder="Any additional notes or special requirements"
            :class="inputClass"
          ></textarea>
        </div>
      </div>
    </div> 
    
    <div class="mt-[22px] grid grid-cols-2 gap-8">
      <PrimaryButton
        @click="handleBack"
        bgColor="bg-gray-400"
        borderColor="border-gray-400"
        class="py-3 text-lg font-bold"
      >
        Back to Dates
      </PrimaryButton>

      <PrimaryButton
        @click="handleNext"
        class="py-3 text-lg font-bold"
        :disabled="!isFormValid"
        :bgColor="!isFormValid ? 'bg-gray-400' : 'bg-[#013C6D]'"
        :borderColor="!isFormValid ? 'border-gray-400' : 'border-[#013C6D]'"
      >
        Review Request
      </PrimaryButton>
    </div>

  </div>
</template>

<style scoped>
/* Scoped style to make the 'Select' placeholder gray */
select:invalid,
select[value="null"] {
  color: #6b7280; /* text-gray-500 */
}
</style>