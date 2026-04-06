<script setup>
/**
 * @file views/equipment-borrowing/steps/ReviewRequest.vue
 * @description Step 4 (final) of the equipment borrowing wizard.
 * Displays a summary of the selected equipment, dates, borrower info,
 * and total cost before submission. Handles request creation and shows
 * a success modal with the transaction number on completion.
 */

import { ref, computed } from "vue";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";
import { MagnifyingGlassIcon } from "@heroicons/vue/24/outline";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { createEquipmentRequest } from "@/api/equipmentService";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  borrowerInfo: Object,
  goBack: Function,
  hasStartedForm: Function,
});

const emit = defineEmits(["start-new-request"]);

const authStore = useAuthStore();
const router = useRouter();
const { t } = useI18n();

// =============================================================================
// MODAL STATE
// =============================================================================
const showModal = ref(false);
const showExitModal = ref(false);
const transactionNo = ref("");

// =============================================================================
// FORMATTERS
// =============================================================================
const formatCurrency = (value) => {
  if (!value) return "₱0";
  return `₱${parseFloat(value).toLocaleString()}`;
};

const formatDisplayDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "2-digit",
    day: "2-digit",
    year: "numeric",
  });
};

const totalCost = computed(() => {
  if (!props.selectedDates || !props.selectedEquipment) {
    return 0;
  }
  const days = props.selectedDates.days || 1;
  return props.selectedEquipment.reduce((total, item) => {
    return total + item.rate * item.quantity * days;
  }, 0);
});

// =============================================================================
// SUBMISSION
// =============================================================================

const isSubmitting = ref(false)

const handleSubmit = async () => {
  isSubmitting.value = true;

  try {
    const payload = {
      resident_id: authStore.residentId,
      contact_person: props.borrowerInfo.contactPerson,
      contact_number: props.borrowerInfo.contactNumber,
      purpose: props.borrowerInfo.purpose,
      borrow_date: new Date(props.selectedDates.borrow).toISOString(),
      return_date: new Date(props.selectedDates.return).toISOString(),
      items: props.selectedEquipment.map((item) => ({
        item_id: item.id,
        quantity: item.quantity,
      })),
      use_autofill: props.borrowerInfo.use_autofill || false,
    };

    const response = await createEquipmentRequest(payload);

    console.log("Request created:", response);

    transactionNo.value = response.transaction_no;
    showModal.value = true;
  } catch (err) {
    console.error("Failed to create request:", err);
    alert("Failed to submit request. Please try again.");
  } finally {
    isSubmitting.value = false;
  }
};

// =============================================================================
// NAVIGATION
// =============================================================================

const handlePageBack = () => props.goBack('info')

const handleDone = () => {
  router.push("/home");
};

const handleBackClick = () => {
  if (props.hasStartedForm && props.hasStartedForm()) {
    showExitModal.value = true;
  } else {
    router.push("/home");
  }
};

const confirmExit = () => {
  showExitModal.value = false;
  router.push("/home");
};

const cancelExit = () => {
  showExitModal.value = false;
};

const handleNewRequest = () => {
  showModal.value = false;
  emit("start-new-request");
};
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- HEADER -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ t('equipmentBorrowingTitle') }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          {{ t('reviewDetails') }}
        </p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div class="flex gap-3 mb-4">
        <!-- LEFT PANEL -->
        <div class="w-1/2 bg-white rounded-2xl shadow-lg border border-gray-200 p-5">
          <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
            <MagnifyingGlassIcon class="w-8 h-8" />
            {{ t('reviewRequest') }}
          </h3>

          <!-- Selected equipment summary -->
          <div class="mt-4">
            <h4 class="text-lg font-bold text-[#013C6D]">{{ t('selectedItemsSummary') }}</h4>
            <ul class="mt-2 space-y-0">
              <li
                v-for="item in selectedEquipment"
                :key="item.id"
                class="flex justify-between text-base text-gray-700"
              >
                <span>{{ item.name }}</span>
                <span class="font-medium">{{ item.quantity }} {{ t('units') }}</span>
              </li>
            </ul>
          </div>

          <!-- Borrowing period -->
          <div class="mt-6">
            <h4 class="text-lg font-bold text-[#013C6D]">{{ t('borrowingPeriod') }}</h4>
            <div
              class="mt-2 flex justify-between text-base text-gray-700 max-w-xs"
            >
              <div>
                <span class="block text-sm">{{ t('borrowDate') }}</span>
                <span class="font-medium">{{
                  formatDisplayDate(selectedDates?.borrow)
                }}</span>
              </div>
              <div>
                <span class="block text-sm">{{ t('returnDate') }}</span>
                <span class="font-medium">{{
                  formatDisplayDate(selectedDates?.return)
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT PANEL -->
        <div class="w-1/2 flex flex-col gap-3">

          <!-- Contact information -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-5">
            <h3 class="text-2xl font-bold text-[#013C6D]">{{ t('contactInformation') }}</h3>
            <div class="mt-4 space-y-2">
              <div class="flex justify-between text-base">
                <span class="text-gray-600">{{ t('contactPerson') }}</span>
                <span class="font-medium text-right">{{
                  borrowerInfo.contactPerson
                }}</span>
              </div>
              <div class="flex justify-between text-base">
                <span class="text-gray-600">{{ t('contactNumber') }}</span>
                <span class="font-medium text-right">{{
                  borrowerInfo.contactNumber
                }}</span>
              </div>
              <div class="flex justify-between text-base">
                <span class="text-gray-600">{{ t('purpose') }}</span>
                <span class="font-medium text-right">{{
                  borrowerInfo.purpose
                }}</span>
              </div>
            </div>
          </div>

          <!-- Total cost display -->
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-5">
            <div class="flex justify-between text-2xl font-bold text-[#013C6D]">
              <span>{{ t('totalCost') }}</span>
              <span>{{ formatCurrency(totalCost) }}</span>
            </div>
          </div>
          <p class="text-center text-base italic text-gray-600 mt-2 mb-1">
            {{ t('payAtCounter') }}
          </p>
        </div>
      </div>
    </div>

    <!-- FOOTER: BUTTONS -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        @click="handlePageBack"
        variant="outline"
        size="md"
        :disabled="isSubmitting"
      >
        {{ t('backToForm') }}
      </Button>
      <Button
        @click="handleSubmit"
        :disabled="isSubmitting"
        :variant="isSubmitting ? 'disabled' : 'secondary'"
        size="md"
      >
        {{ isSubmitting ? t('submitting') : t('submitRequest') }}
      </Button>
    </div>

    <Transition name="fade-blur">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          :title="t('requestSubmitted')"
          :message="t('requestSubmittedMsg')"
          :referenceId="transactionNo"
          :showReferenceId="true"
          :primaryButtonText="t('done')"
          :showPrimaryButton="true"
          :showSecondaryButton="false"
          :showNewRequest="true"
          @primary-click="handleDone"
          @new-request="handleNewRequest"
        />
      </div>
    </Transition>

    <Transition name="fade-blur">
      <div
        v-if="showExitModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          :title="t('exitEquipmentRequest')"
          :message="t('unsavedChanges')"
          type="warning"
          :primaryButtonText="t('exit')"
          :secondaryButtonText="t('stay')"
          :showPrimaryButton="true"
          :showSecondaryButton="true"
          :showReferenceId="false"
          @primary-click="confirmExit"
          @secondary-click="cancelExit"
        />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.modal-backdrop {
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    -webkit-backdrop-filter 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  -webkit-backdrop-filter: blur(0px);
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
</style>