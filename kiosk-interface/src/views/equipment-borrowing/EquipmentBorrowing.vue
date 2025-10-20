<script setup>
// 1. You MUST import 'onActivated' from 'vue'
import { ref, onActivated } from 'vue'

// Step components (statically imported)
import EquipmentSelect from './steps/SelectEquipment.vue'
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

const onUpdateEquipment = (newEquipmentArray) => {
  selectedEquipment.value = newEquipmentArray
}

const onUpdateDates = (newDatesObject) => {
  selectedDates.value = newDatesObject
}

// 2. You MUST add this 'onActivated' block
// This hook runs every time you navigate TO this component
// if it is being kept alive by <KeepAlive>.
onActivated(() => {
  // Reset all the data to its starting state
  selectedEquipment.value = []
  selectedDates.value = null
  borrowerInfo.value = {}
  currentStep.value = 'select'
})

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
    @update:selected-equipment="onUpdateEquipment"

    :selected-dates="selectedDates"
    @update:selected-dates="onUpdateDates"

    :borrower-info="borrowerInfo"
    :go-next="goNext"
    :go-back="goBack"
  />
</template>