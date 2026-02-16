<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";

const router = useRouter();
const reason = ref("");
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const referenceId = ref("");

const goBack = () => router.push("/id-services");

const submitRequest = () => {
  if (!reason.value) return;
  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    referenceId.value = `REQ-${Math.floor(100000 + Math.random() * 900000)}`;
    showSuccessModal.value = true;
  }, 1500);
};

const handleModalDone = () => router.push("/id-services");
const handleNewRequest = () => {
  reason.value = "";
  referenceId.value = "";
  showSuccessModal.value = false;
};
</script>

<template>
  <div
    class="flex flex-col w-full h-full bg-white transition-all duration-300 overflow-hidden select-none no-scrollbar"
  >
    <div v-if="!showSuccessModal" class="flex flex-col h-full">
      <div class="flex items-center mb-0 gap-7 flex-shrink-0">
        <ArrowBackButton @click="goBack" />
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Request Replacement
          </h1>
          <p class="text-[#03335C] -mt-2">
            Submit a request for a new physical RFID card.
          </p>
        </div>
      </div>

      <div class="flex-1 flex flex-col items-center justify-center pb-0">
        <div
          class="w-full max-w-2xl bg-white pt-6 pb-8 px-8 rounded-3xl shadow-[0_5px_15px_-5px_rgba(0,0,0,0.08)] border border-gray-100"
        >
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-[#03335C] mb-1">
              Replacement Details
            </h2>
            <p class="text-gray-500 text-lg">
              A replacement fee of
              <span class="font-bold text-[#03335C]">₱150.00</span> applies.
            </p>
          </div>

          <div class="space-y-6">
            <div>
              <label
                class="block text-xs font-bold text-[#03335C] mb-3 uppercase tracking-wider"
              >
                Reason for Request
              </label>
              <div class="relative">
                <select
                  v-model="reason"
                  class="w-full p-5 rounded-xl border-2 border-gray-200 bg-gray-50 text-xl text-[#03335C] focus:border-[#21C05C] focus:bg-white outline-none transition-all appearance-none cursor-pointer font-medium"
                >
                  <option value="" disabled>Select a reason...</option>
                  <option value="damaged">Damaged / Broken Card</option>
                  <option value="lost">Lost Card</option>
                  <option value="expired">Expired Card</option>
                  <option value="info_change">Change of Information</option>
                  <option value="faded">Faded / Unreadable</option>
                </select>
                <div
                  class="absolute inset-y-0 right-5 flex items-center pointer-events-none"
                >
                  <svg
                    class="w-6 h-6 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 9l-7 7-7-7"
                    ></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="pt-1">
              <Button
                @click="submitRequest"
                :disabled="!reason || isSubmitting"
                :variant="!reason || isSubmitting ? 'disabled' : 'primary'"
                class="w-full py-5 text-xl font-bold"
              >
                {{ isSubmitting ? "Processing..." : "Submit Request" }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="h-full flex items-center justify-center">
      <Modal
        title="Request Submitted!"
        message="Your replacement request has been successfully queued. Please proceed to the Barangay Hall Cashier for payment."
        :reference-id="referenceId"
        :show-reference-id="true"
        :show-secondary-button="true"
        secondary-button-text="New Request"
        @secondary-click="handleNewRequest"
        primary-button-text="Done"
        @primary-click="handleModalDone"
      />
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
