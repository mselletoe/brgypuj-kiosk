<script setup>
import { ref } from 'vue'

// Step components (statically imported)
import EquipmentSelect from './steps/SelectEquipments.vue'
import EquipmentSelectDates from './steps/SelectDates.vue'
import EquipmentForm from './steps/BorrowerInfo.vue'
import EquipmentReviewRequest from './steps/ReviewRequest.vue'

// Shared state across steps
const selectedEquipment = ref([])
const selectedDates = ref(null)
const borrowerInfo = ref({})

// Current step
const currentStep = ref('select')

// Navigate steps
const goNext = (step) => currentStep.value = step
const goBack = (step) => currentStep.value = step

// Map step names to components
const components = {
  select: EquipmentSelect,
  dates: EquipmentSelectDates,
  info: EquipmentForm,
  review: EquipmentReviewRequest,
}
</script>

<template>
  <component
    :is="components[currentStep]"
    :selected-equipment="selectedEquipment"
    :selected-dates="selectedDates"
    :borrower-info="borrowerInfo"
    :go-next="goNext"
    :go-back="goBack"
  />
</template>