<script setup>
import { ref, onActivated } from 'vue';
import EquipmentSelect from './steps/SelectEquipment.vue';
import EquipmentSelectDates from './steps/SelectDates.vue';
import EquipmentForm from './steps/BorrowerInfo.vue';
import EquipmentReviewRequest from './steps/ReviewRequest.vue';

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