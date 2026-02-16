<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";
import {
  BackspaceIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  KeyIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();

// Step Logic
const step = ref(1);
const pinBuffer = ref("");
const currentPin = ref("");
const newPin = ref("");
const confirmPin = ref("");

const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const pinLength = 6;

const stepInfo = computed(() => {
  if (step.value === 1)
    return {
      title: "Verify Identity",
      desc: "Please enter your current 6-digit passcode to authorize this change.",
      icon: LockClosedIcon,
    };
  if (step.value === 2)
    return {
      title: "New Passcode",
      desc: "Create a new 6-digit security PIN. Avoid using simple sequences.",
      icon: KeyIcon,
    };
  return {
    title: "Confirm PIN",
    desc: "Enter your new passcode one more time to confirm.",
    icon: ShieldCheckIcon,
  };
});

const handleKeypad = (num) => {
  if (pinBuffer.value.length < pinLength) pinBuffer.value += num;
};

const handleBackspace = () => {
  pinBuffer.value = pinBuffer.value.slice(0, -1);
};

const goBack = () => {
  if (step.value > 1) {
    step.value--;
    pinBuffer.value = "";
  } else {
    router.push("/id-services");
  }
};

const handleNext = () => {
  if (pinBuffer.value.length !== pinLength) return;

  if (step.value === 1) {
    currentPin.value = pinBuffer.value;
    step.value = 2;
    pinBuffer.value = "";
  } else if (step.value === 2) {
    newPin.value = pinBuffer.value;
    step.value = 3;
    pinBuffer.value = "";
  } else if (step.value === 3) {
    if (newPin.value !== pinBuffer.value) {
      alert("Passcodes do not match!");
      pinBuffer.value = "";
      return;
    }
    submitChange();
  }
};

const submitChange = () => {
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
            Change Passcode
          </h1>
          <p class="text-[#03335C] -mt-2">
            Secure your account by updating your security PIN.
          </p>
        </div>
      </div>

      <div
        class="flex-1 flex flex-row items-stretch justify-center gap-10 px-4 pt-8 pb-12"
      >
        <div class="flex-1 max-w-[420px] flex flex-col">
          <div
            class="bg-blue-50/50 p-8 rounded-3xl border border-blue-100/50 flex flex-col h-full shadow-sm"
          >
            <div class="flex-1">
              <component
                :is="stepInfo.icon"
                class="w-10 h-10 text-[#03335C] mb-4"
              />
              <h2 class="text-3xl font-bold text-[#03335C] mb-2">
                {{ stepInfo.title }}
              </h2>
              <p class="text-gray-500 text-base leading-snug mb-6">
                {{ stepInfo.desc }}
              </p>

              <div class="flex gap-2">
                <div
                  v-for="i in 3"
                  :key="i"
                  :class="[
                    'h-2 rounded-full transition-all duration-300',
                    step === i ? 'w-8 bg-[#03335C]' : 'w-2 bg-gray-300',
                  ]"
                ></div>
              </div>
            </div>

            <Button
              @click="handleNext"
              :disabled="pinBuffer.length !== pinLength || isSubmitting"
              :variant="
                pinBuffer.length !== pinLength || isSubmitting
                  ? 'disabled'
                  : 'primary'
              "
              class="w-full py-5 text-xl font-bold shadow-md shadow-blue-900/10"
            >
              {{
                isSubmitting
                  ? "Processing..."
                  : step === 3
                    ? "Confirm Change"
                    : "Next Step"
              }}
            </Button>
          </div>
        </div>

        <div class="flex-1 max-w-[380px] flex flex-col">
          <div
            class="bg-white p-7 rounded-3xl shadow-[0_5px_15px_-5px_rgba(0,0,0,0.08)] border border-gray-100 flex flex-col items-center h-full justify-center"
          >
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
                class="h-14 rounded-2xl bg-gray-50 text-[#03335C] flex items-center justify-center active:bg-orange-50 active:text-orange-600 transition-colors"
              >
                <BackspaceIcon class="w-7 h-7" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Modal
      v-else
      title="Passcode Updated!"
      message="Your security PIN has been successfully changed."
      primary-button-text="Done"
      @primary-click="handleModalDone"
    />
  </div>
</template>
