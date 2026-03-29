<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useIDApplication } from "@/composables/useIDApplication";

import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";

import SelectionPhase from "./phases/SelectionPhase.vue";
import DetailsPhase from "./phases/DetailsPhase.vue";
import CameraPhase from "./phases/CameraPhase.vue";

import VerificationModal from "./modals/VerificationModal.vue";
import RequirementsModal from "./modals/RequirementsModal.vue";
import SuccessModal from "./modals/SuccessModal.vue";
import ErrorModal from "./modals/ErrorModal.vue";
import PendingModal from "./modals/PendingModal.vue";

const { t } = useI18n();

// Composable — all state & logic lives here
const {
  currentPhase,

  lastNameLetter,
  firstNameLetter,
  selectedResident,
  residentList,
  isFetching,
  fetchResidents,
  resetSelection,
  proceedToVerification,

  showVerificationModal,
  verifyMonth,
  verifyDay,
  verifyYear,
  verificationError,
  isVerifying,
  handleVerification,

  showRequirementsModal,
  requirementsChecks,
  isEligible,
  isCheckingRequirements,
  proceedFromRequirements,

  idFields,
  detailsForm,
  detailsErrors,
  useManualEntry,
  isFetchingAutofill,
  brgyIdNumber,
  loadIDFields,
  proceedToCameraFromDetails,
  AUTOFILL_MAP,

  isSubmitting,
  submitApplication,

  showSuccessModal,
  showErrorModal,
  showPendingModal,
  referenceId,

  goBack,
  handleModalDone,
} = useIDApplication();

// Ref to CameraPhase so we can call stopCamera() when navigating back
const cameraPhaseRef = ref(null);
const isCountingDown = ref(false);

function handleGoBack() {
  if (currentPhase.value === "camera") {
    cameraPhaseRef.value?.stopCamera();
  }
  goBack(isCountingDown.value);
}

async function handleCameraSubmit(photo) {
  await submitApplication(photo);
}

onMounted(loadIDFields);
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleGoBack" :disabled="isCountingDown" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ t("applyForRFID") }}
        </h1>
        <p class="text-[#03335C] -mt-2">{{ t("selectResidentRecord") }}</p>
      </div>
    </div>

    <!-- Main card -->
    <div class="flex-1 mb-4 min-h-0">
      <div
        :class="currentPhase === 'details' ? 'h-full' : ''"
        class="w-full bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex flex-col transition-all duration-500 ease-in-out"
      >
        <SelectionPhase
          v-if="currentPhase === 'selection'"
          :last-name-letter="lastNameLetter"
          :first-name-letter="firstNameLetter"
          :selected-resident="selectedResident"
          :resident-list="residentList"
          :is-fetching="isFetching"
          @update:lastNameLetter="lastNameLetter = $event"
          @update:firstNameLetter="firstNameLetter = $event"
          @update:selectedResident="selectedResident = $event"
          @fetch-residents="fetchResidents"
        />

        <DetailsPhase
          v-else-if="currentPhase === 'details'"
          :id-fields="idFields"
          :details-form="detailsForm"
          :details-errors="detailsErrors"
          :use-manual-entry="useManualEntry"
          :is-fetching-autofill="isFetchingAutofill"
          :is-submitting="isSubmitting"
          :autofill-map="AUTOFILL_MAP"
          @update:detailsForm="detailsForm = $event"
          @update:useManualEntry="useManualEntry = $event"
        />

        <CameraPhase
          v-else-if="currentPhase === 'camera'"
          ref="cameraPhaseRef"
          :selected-resident="selectedResident"
          :brgy-id-number="brgyIdNumber"
          :is-submitting="isSubmitting"
          @submit="handleCameraSubmit"
          @counting-down="isCountingDown = $event"
        />
      </div>
    </div>

    <!-- Bottom action bar -->
    <div
      v-if="currentPhase === 'selection'"
      class="flex gap-6 mt-6 justify-between items-center flex-shrink-0"
    >
      <Button
        variant="outline"
        size="md"
        @click="resetSelection"
        :disabled="!lastNameLetter && !firstNameLetter && !selectedResident"
        >{{ t("resetSelection") }}</Button
      >
      <Button
        :variant="selectedResident ? 'secondary' : 'disabled'"
        size="md"
        :disabled="!selectedResident"
        @click="proceedToVerification"
        >{{ t("continueToForm") }}</Button
      >
    </div>

    <div
      v-else-if="currentPhase === 'details'"
      class="flex gap-6 mt-6 justify-between items-center flex-shrink-0"
    >
      <Button variant="outline" size="md" @click="currentPhase = 'selection'">{{
        t("back")
      }}</Button>
      <Button
        variant="secondary"
        size="md"
        @click="proceedToCameraFromDetails"
        >{{ t("nextTakePhoto") }}</Button
      >
    </div>

    <!-- Modals -->
    <VerificationModal
      v-if="showVerificationModal"
      :selected-resident="selectedResident"
      :verify-month="verifyMonth"
      :verify-day="verifyDay"
      :verify-year="verifyYear"
      :verification-error="verificationError"
      :is-verifying="isVerifying"
      @update:verifyMonth="verifyMonth = $event"
      @update:verifyDay="verifyDay = $event"
      @update:verifyYear="verifyYear = $event"
      @verify="handleVerification"
      @close="showVerificationModal = false"
    />

    <RequirementsModal
      v-if="showRequirementsModal"
      :selected-resident="selectedResident"
      :requirements-checks="requirementsChecks"
      :is-eligible="isEligible"
      :is-checking-requirements="isCheckingRequirements"
      @proceed="proceedFromRequirements"
      @close="showRequirementsModal = false"
    />

    <SuccessModal
      v-if="showSuccessModal"
      :reference-id="referenceId"
      @done="handleModalDone"
    />

    <ErrorModal v-if="showErrorModal" @close="showErrorModal = false" />

    <PendingModal v-if="showPendingModal" @close="showPendingModal = false" />
  </div>
</template>
