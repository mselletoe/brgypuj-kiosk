<script setup>
import { ref, computed } from 'vue';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import PrimaryButton from '@/components/shared/PrimaryButton.vue';
import Modal from '@/components/shared/Modal.vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';
import { useRouter } from 'vue-router';
import { createKioskRequest } from '@/api/equipmentApi'; // <-- Import API

const props = defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  borrowerInfo: Object,
  goBack: Function,
});

const emit = defineEmits(['start-new-request']);

const router = useRouter();
const showModal = ref(false);
const isSubmitting = ref(false); // <-- Add loading state

const formatCurrency = (value) => {
  if (!value) return '₱0';
  // Use 'P' for Pesos
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

const handleModalNewRequest = () => {
  showModal.value = false;
  emit('start-new-request');
};

// --- MODIFIED: handleSubmit is now async and calls the API ---
const handleSubmit = async () => {
  isSubmitting.value = true;
  
  // 1. We must rename 'return' to 'return_date' for the backend
  const datesPayload = {
    borrow: props.selectedDates.borrow.toISOString(),
    return_date: props.selectedDates.return.toISOString(), // <-- Renamed
    days: props.selectedDates.days
  };
  
  // 2. We only need id and quantity for the equipment
  const equipmentPayload = props.selectedEquipment.map(item => ({
    id: item.id,
    quantity: item.quantity
  }));

  // 3. This is the final object to send
  const payload = {
    equipment: equipmentPayload,
    dates: datesPayload,
    info: props.borrowerInfo,
    total: totalCost.value,
  };

  try {
    // 4. Call the API
    const result = await createKioskRequest(payload);
    console.log('Request successful:', result);
    // Show the success modal
    showModal.value = true;
  } catch (error) {
    console.error('Failed to submit request:', error);
    // Show an error to the user
    alert(`Error: ${error.message}\nPlease try again.`);
  } finally {
    isSubmitting.value = false;
  }
};
// --- END OF MODIFICATION ---

const handleModalDone = () => {
  showModal.value = false;
  router.push('/home');
};
</script>

<template>
  <div class="py-0 p-8">
    <div class="flex items-center gap-4">
      <ArrowBackButton @click="handlePageBack" />
      <h1 class="text-[40px] font-bold text-[#013C6D]">Equipment Borrowing</h1>
    </div>

    <div class="mt-6 flex gap-2 items-start">
      <div class="w-1/2 bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
          <MagnifyingGlassIcon class="w-8 h-8" />
          Review Your Request
        </h3>
        <div class="mt-6">
          <h4 class="text-lg font-bold text-[#013C6D]">Selected Items Summary</h4>
          <ul class="mt-2 space-y-0 min-h-24">
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

      <div class="w-1/2 flex flex-col gap-2">
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
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
            <div class="flex justify-between text-base">
              <span class="text-gray-600">Additional Notes</span>
              <span class="font-medium text-right break-all">{{ borrowerInfo.notes || 'N/A' }}</span>
            </div>
          </div>
        </div>
        <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6">
          <div class="flex justify-between text-2xl font-bold text-[#013C6D]">
            <span>Total Cost:</span>
            <span>{{ formatCurrency(totalCost) }}</span>
          </div>
        </div>
        <p class="text-center text-base italic text-gray-600 mt-0 mb-1">
          Please pay the fee at the counter.
        </p>
      </div>
    </div>

    <div class="mt-[11px] grid grid-cols-2 gap-8">
      <PrimaryButton
        @click="handlePageBack"
        bgColor="bg-gray-400"
        borderColor="border-gray-400"
        class="py-3 text-lg font-bold"
        :disabled="isSubmitting"
      >
        Back to Form
      </PrimaryButton>
      <PrimaryButton
        @click="handleSubmit"
        class="py-3 text-lg font-bold"
        :disabled="isSubmitting"
        :bgColor="isSubmitting ? 'bg-gray-400' : 'bg-[#013C6D]'"
        :borderColor="isSubmitting ? 'border-gray-400' : 'border-[#013C6D]'"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
      </PrimaryButton>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
      <Modal
        title="Request Submitted!"
        message="Your borrowing request has been submitted for approval. Pay the fee at the counter and you will be contacted for pickup details."
        :showNewRequest="true"
        newRequestText="New Request"
        @done="handleModalDone"
        @newRequest="handleModalNewRequest"
      />
    </div>
  </div>
</template>