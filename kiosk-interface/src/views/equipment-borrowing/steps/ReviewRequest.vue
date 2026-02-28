<script setup>
import { ref, computed } from 'vue';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import Button from '@/components/shared/Button.vue';
import Modal from '@/components/shared/Modal.vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';
import { useRouter } from 'vue-router';
import { createEquipmentRequest } from '@/api/equipmentService';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

const props = defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  borrowerInfo: Object,
  goBack: Function,
  hasStartedForm: Function,
});

const emit = defineEmits(['start-new-request']);

const showModal = ref(false);
const showExitModal = ref(false);
const isSubmitting = ref(false);
const transactionNo = ref('');
const isFadingOut = ref(false);

const formatCurrency = (value) => {
  if (!value) return '₱0';
  return `₱${parseFloat(value).toLocaleString()}`;
};

const formatDisplayDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
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

const handlePageBack = () => {
   props.goBack('info');
};

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
      items: props.selectedEquipment.map(item => ({
        item_id: item.id,
        quantity: item.quantity
      })),
      use_autofill: props.borrowerInfo.use_autofill || false
    };

    const response = await createEquipmentRequest(payload);

    console.log('Request created:', response);

    transactionNo.value = response.transaction_no;
    showModal.value = true;

  } catch (err) {
    console.error('Failed to create request:', err);
    alert('Failed to submit request. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};

const handleDone = () => {
  router.push('/home');
};

const handleBackClick = () => {
  if (props.hasStartedForm && props.hasStartedForm()) {
    showExitModal.value = true;
  } else {
    router.push('/home');
  }
};

const confirmExit = () => {
  showExitModal.value = false;
  router.push('/home');
};

const cancelExit = () => {
  showExitModal.value = false;
};
</script>

<template>
  <div class="flex flex-col w-full h-full" :class="{ 'content-with-keyboard': showKeyboard }">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Equipment Borrowing</h1>
        <p class="text-[#03335C] -mt-2">Review the details of your equipment request.</p>
      </div>
    </div>

    <!-- Main -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="flex gap-3 mb-4">
        <!-- Left -->
        <div class="w-1/2 bg-white rounded-2xl shadow-lg border border-gray-200 p-5">
          <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
            <MagnifyingGlassIcon class="w-8 h-8" />
            Review Your Request
          </h3>
          <div class="mt-4">
            <h4 class="text-lg font-bold text-[#013C6D]">Selected Items Summary</h4>
            <ul class="mt-2 space-y-0">
              <li
                v-for="item in selectedEquipment"
                :key="item.id"
                class="flex justify-between text-base text-gray-700"
              >
                <span>{{ item.name }}</span>
                <span class="font-medium">{{ item.quantity }} units</span>
              </li>
            </ul>
          </div>
          <div class="mt-6">
            <h4 class="text-lg font-bold text-[#013C6D]">Borrowing Period</h4>
            <div class="mt-2 flex justify-between text-base text-gray-700 max-w-xs">
              <div>
                <span class="block text-sm">Borrow Date</span>
                <span class="font-medium">{{ formatDisplayDate(selectedDates?.borrow) }}</span>
              </div>
              <div>
                <span class="block text-sm">Return Date</span>
                <span class="font-medium">{{ formatDisplayDate(selectedDates?.return) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right -->
        <div class="w-1/2 flex flex-col gap-3">
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-5">
            <h3 class="text-2xl font-bold text-[#013C6D]">Contact Information</h3>
            <div class="mt-4 space-y-2">
              <div class="flex justify-between text-base">
                <span class="text-gray-600">Contact Person</span>
                <span class="font-medium text-right">{{ borrowerInfo.contactPerson }}</span>
              </div>
              <div class="flex justify-between text-base">
                <span class="text-gray-600">Contact Number</span>
                <span class="font-medium text-right">{{ borrowerInfo.contactNumber }}</span>
              </div>
              <div class="flex justify-between text-base">
                <span class="text-gray-600">Purpose</span>
                <span class="font-medium text-right">{{ borrowerInfo.purpose }}</span>
              </div>
            </div>
          </div>
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-5">
            <div class="flex justify-between text-2xl font-bold text-[#013C6D]">
              <span>Total Cost:</span>
              <span>{{ formatCurrency(totalCost) }}</span>
            </div>
          </div>
          <p class="text-center text-base italic text-gray-600 mt-2 mb-1">
            Please pay the fee at the counter.
          </p>
        </div>
      </div>
    </div>

    <!-- Buttons -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        @click="handlePageBack"
        variant="outline"
        size="md"
        :disabled="isSubmitting"
      >
        Back to Form
      </Button>
      <Button
        @click="handleSubmit"
        :disabled="isSubmitting"
        :variant="isSubmitting ? 'disabled' : 'secondary'"
        size="md"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
      </Button>
    </div>

    <!-- Success Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
      <Modal
        title="Request Submitted!"
        :message="`Pay the fee at the counter and you will be contacted for pickup details. Please take note of the Request ID number below for reference.`"
        :referenceId="transactionNo"
        :showReferenceId="true"
        primaryButtonText="Done"
        :showPrimaryButton="true"
        :showSecondaryButton="false"
        :showNewRequest="false"
        @primary-click="handleDone"
      />
    </div>

    <!-- Exit Confirmation Modal -->
    <div v-if="showExitModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
      <Modal
        title="Exit Equipment Request?"
        message="You have unsaved changes. Are you sure you want to exit? All your progress will be lost."
        primaryButtonText="Exit"
        secondaryButtonText="Stay"
        :showPrimaryButton="true"
        :showSecondaryButton="true"
        :showReferenceId="false"
        @primary-click="confirmExit"
        @secondary-click="cancelExit"
      />
    </div>
  </div>
</template>