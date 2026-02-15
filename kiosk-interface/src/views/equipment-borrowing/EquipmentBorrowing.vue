<script setup>
import { ref, onActivated } from 'vue';
import EquipmentSelect from './steps/SelectEquipment.vue';
import EquipmentSelectDates from './steps/SelectDates.vue';
import EquipmentForm from './steps/BorrowerInfo.vue';
import EquipmentReviewRequest from './steps/ReviewRequest.vue';

const selectedEquipment = ref([]);
const selectedDates = ref(null);

const borrowerInfo = ref({
  contactPerson: '',
  contactNumber: '',
  purpose: null,
  notes: '',
  use_autofill: false
});

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

const hasStartedForm = () => {
  return selectedEquipment.value.length > 0 || 
         selectedDates.value !== null || 
         borrowerInfo.value.contactPerson ||
         borrowerInfo.value.contactNumber ||
         borrowerInfo.value.purpose ||
         borrowerInfo.value.notes;
};

onActivated(() => {
  resetFormAndGoToStart();
});
</script>

<template>
  <EquipmentSelect 
    v-if="currentStep === 'select'"
    :selected-equipment="selectedEquipment"
    @update:selected-equipment="onUpdateEquipment"
    :go-next="goNext"
    :has-started-form="hasStartedForm"
  />

  <EquipmentSelectDates
    v-if="currentStep === 'dates'"
    :selected-equipment="selectedEquipment"
    :selected-dates="selectedDates"
    @update:selected-dates="onUpdateDates"
    :go-next="goNext"
    :go-back="goBack"
    :has-started-form="hasStartedForm"
  />

  <EquipmentForm
    v-if="currentStep === 'info'"
    :borrower-info="borrowerInfo"
    @update:borrower-info="onUpdateBorrowerInfo"
    :go-next="goNext"
    :go-back="goBack"
    :has-started-form="hasStartedForm"
  />

  <EquipmentReviewRequest
    v-if="currentStep === 'review'"
    :selected-equipment="selectedEquipment"
    :selected-dates="selectedDates"
    :borrower-info="borrowerInfo"
    :go-back="goBack"
    @start-new-request="resetFormAndGoToStart"
    :has-started-form="hasStartedForm"
  />
</template>