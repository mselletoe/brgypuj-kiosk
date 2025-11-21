<script setup>
import { ref, onActivated, computed } from 'vue';
import EquipmentSelect from './steps/SelectEquipment.vue';
import EquipmentSelectDates from './steps/SelectDates.vue';
import EquipmentForm from './steps/BorrowerInfo.vue';
import EquipmentReviewRequest from './steps/ReviewRequest.vue';

// Import the auth store
import { auth } from '@/stores/auth.js'; 

const selectedEquipment = ref([]);
const selectedDates = ref(null);
const borrowerInfo = ref({});
const currentStep = ref('select');

const goNext = (step) => currentStep.value = step;
const goBack = (step) => currentStep.value = step;

const onUpdateEquipment = (newEquipmentArray) => {
  selectedEquipment.value = newEquipmentArray;
};
const onUpdateDates = (newDatesObject) => {
  selectedDates.value = newDatesObject;
};
const onUpdateBorrowerInfo = (newInfoObject) => {
  borrowerInfo.value = newInfoObject;
};

const resetFormAndGoToStart = () => {
  selectedEquipment.value = [];
  selectedDates.value = null;
  borrowerInfo.value = {};
  currentStep.value = 'select';
};

onActivated(() => {
  resetFormAndGoToStart();
});

// --- THIS IS THE FIX ---
const authInfo = computed(() => {
  // Check that auth.user exists and is not a guest
  if (auth.user && !auth.isGuest) { 
    return {
      resident_id: auth.user.id,
      
      // MODIFIED: Read the 'rfid_uid' directly from the root auth.user object
      rfid: auth.user.rfid_uid || null, 
      
      contactPerson: `${auth.user.first_name} ${auth.user.last_name}`,
      contactNumber: auth.user.phone_number
    }
  }
  return null;
});
// --- END OF FIX ---
</script>

<template>
  <EquipmentSelect 
    v-if="currentStep === 'select'"
    :selected-equipment="selectedEquipment"
    @update:selected-equipment="onUpdateEquipment"
    :go-next="goNext"
  />

  <EquipmentSelectDates
    v-if="currentStep === 'dates'"
    :selected-equipment="selectedEquipment"
    :selected-dates="selectedDates"
    @update:selected-dates="onUpdateDates"
    :go-next="goNext"
    :go-back="goBack"
  />

  <EquipmentForm
    v-if="currentStep === 'info'"
    :borrower-info="borrowerInfo"
    @update:borrower-info="onUpdateBorrowerInfo"
    :go-next="goNext"
    :go-back="goBack"
    :auth-info="authInfo"
  />

  <EquipmentReviewRequest
    v-if="currentStep === 'review'"
    :selected-equipment="selectedEquipment"
    :selected-dates="selectedDates"
    :borrower-info="borrowerInfo"
    :go-back="goBack"
    @start-new-request="resetFormAndGoToStart"
  />
</template>