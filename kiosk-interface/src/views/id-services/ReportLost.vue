<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";
import {
  BackspaceIcon,
  ExclamationTriangleIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();

const pinBuffer = ref("");
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const pinLength = 6;

const handleKeypad = (num) => {
  if (pinBuffer.value.length < pinLength) pinBuffer.value += num;
};

const handleBackspace = () => {
  pinBuffer.value = pinBuffer.value.slice(0, -1);
};

const goBack = () => router.push("/id-services");

const submitReport = () => {
  if (pinBuffer.value.length !== pinLength) return;

  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    showSuccessModal.value = true;
  }, 1500);
};

const handleModalDone = () => router.push("/id-services");
</script>

<template>
  <div
    class="flex flex-col w-full h-full bg-white overflow-hidden select-none no-scrollbar"
  >
    <div v-if="!showSuccessModal" class="flex flex-col h-full">
      <div class="flex items-center mb-0 gap-7 flex-shrink-0">
        <ArrowBackButton @click="goBack" />
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Report Lost Card
          </h1>
          <p class="text-[#03335C] -mt-2">
            Deactivate your RFID card immediately to prevent unauthorized use.
          </p>
        </div>
      </div>

      <div
        class="flex-1 flex flex-row items-stretch justify-center gap-10 px-4 pt-4 pb-12"
      >
        <div class="flex-1 max-w-[420px] flex flex-col">
          <div
            class="bg-red-50 p-8 rounded-3xl border border-red-100 flex flex-col h-full shadow-sm"
          >
            <div class="flex-1">
              <ExclamationTriangleIcon class="w-12 h-12 text-red-600 mb-4" />
              <h2 class="text-3xl font-bold text-[#03335C] mb-2">
                Critical Action
              </h2>
              <p class="text-gray-600 text-base leading-snug mb-4">
                Reporting your card as lost will
                <span class="font-bold text-red-600 uppercase"
                  >permanently disable</span
                >
                its RFID functions.
              </p>
              <p class="text-gray-500 text-sm leading-snug">
                You will need to request a replacement card at the Barangay Hall
                to regain access.
              </p>
            </div>

            <Button
              @click="submitReport"
              :disabled="pinBuffer.length !== pinLength || isSubmitting"
              :variant="
                pinBuffer.length !== pinLength || isSubmitting
                  ? 'disabled'
                  : 'primary'
              "
              class="w-full py-5 text-xl font-bold shadow-md !bg-red-600 hover:!bg-red-700 disabled:!bg-gray-200"
            >
              {{ isSubmitting ? "Processing..." : "Confirm & Block" }}
            </Button>
          </div>
        </div>

        <div class="flex-1 max-w-[380px] flex flex-col">
          <div
            class="bg-white p-7 rounded-3xl shadow-[0_5px_15px_-5px_rgba(0,0,0,0.08)] border border-gray-100 flex flex-col items-center h-full justify-center"
          >
            <p
              class="text-[#03335C] font-bold mb-5 uppercase tracking-widest text-[10px] opacity-60"
            >
              Security Verification
            </p>

            <div class="flex gap-4 mb-8">
              <div
                v-for="i in pinLength"
                :key="i"
                :class="[
                  'w-4 h-4 rounded-full border-2 transition-all',
                  pinBuffer.length >= i
                    ? 'bg-[#03335C] border-[#03335C]'
                    : 'bg-transparent border-gray-300',
                ]"
              ></div>
            </div>

            <div class="grid grid-cols-3 gap-3 w-full">
              <button
                v-for="n in 9"
                :key="n"
                @click="handleKeypad(n.toString())"
                class="h-14 rounded-2xl bg-gray-50 text-[#03335C] text-2xl font-bold border border-gray-100 active:bg-gray-200 transition-colors"
              >
                {{ n }}
              </button>
              <div class="h-14"></div>
              <button
                @click="handleKeypad('0')"
                class="h-14 rounded-2xl bg-gray-50 text-[#03335C] text-2xl font-bold border border-gray-100 active:bg-gray-200 transition-colors"
              >
                0
              </button>
              <button
                @click="handleBackspace"
                class="h-14 rounded-2xl bg-gray-50 text-[#03335C] flex items-center justify-center active:bg-red-50 active:text-red-600 transition-colors"
              >
                <BackspaceIcon class="w-8 h-8" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Modal
      v-else
      title="Card Deactivated"
      message="Your RFID card has been successfully blocked for security purposes."
      primary-button-text="Done"
      @primary-click="handleModalDone"
    />
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
