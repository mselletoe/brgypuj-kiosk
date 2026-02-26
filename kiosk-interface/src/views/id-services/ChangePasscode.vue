<script setup>
import { ref, computed, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { changePin } from "@/api/idService";
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
const authStore = useAuthStore();

// Step Logic
const step = ref(1);
const pinBuffer = ref("");
const currentPin = ref("");
const newPin = ref("");
const confirmPin = ref("");

const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const isShaking = ref(false);
const verificationError = ref("");
const pinLength = 4;

const stepInfo = computed(() => {
  if (step.value === 1)
    return {
      title: "Verify Identity",
      desc: "Please enter your current 4-digit passcode to authorize this change.",
      icon: LockClosedIcon,
    };
  if (step.value === 2)
    return {
      title: "New Passcode",
      desc: "Create a new 4-digit security PIN. Avoid using simple sequences.",
      icon: KeyIcon,
    };
  return {
    title: "Confirm PIN",
    desc: "Enter your new passcode one more time to confirm.",
    icon: ShieldCheckIcon,
  };
});

const handleKeypad = (num) => {
  if (pinBuffer.value.length < pinLength) {
    pinBuffer.value += num;
    verificationError.value = "";
  }
};

const handleBackspace = () => {
  pinBuffer.value = pinBuffer.value.slice(0, -1);
  verificationError.value = "";
};

const goBack = () => {
  if (step.value > 1) {
    step.value--;
    pinBuffer.value = "";
    verificationError.value = "";
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
      isShaking.value = true;
      verificationError.value = "Passcodes do not match!";
      setTimeout(() => {
        isShaking.value = false;
        pinBuffer.value = "";
      }, 500);
      return;
    }
    submitChange();
  }
};

const submitChange = async () => {
  isSubmitting.value = true;
  try {
    await changePin({
      resident_id: authStore.residentId,
      current_pin: currentPin.value,
      new_pin: newPin.value,
    });
    showSuccessModal.value = true;
  } catch (err) {
    const status = err?.response?.status;
    const detail = err?.response?.data?.detail || "Something went wrong. Please try again.";

    if (status === 401) {
      // Wrong current PIN — send user back to step 1 with error
      step.value = 1;
      pinBuffer.value = "";
      currentPin.value = "";
      newPin.value = "";
      confirmPin.value = "";
      isShaking.value = true;
      verificationError.value = "Incorrect current passcode.";
      setTimeout(() => { isShaking.value = false; }, 500);
    } else {
      verificationError.value = detail;
      isShaking.value = true;
      setTimeout(() => { isShaking.value = false; pinBuffer.value = ""; }, 500);
    }
  } finally {
    isSubmitting.value = false;
  }
};

const handleModalDone = () => router.push("/id-services");
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
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

    <!-- Main -->
    <div class="flex-1 flex flex-row items-stretch justify-center gap-8 animate-fadeIn mb-4">
      <!-- Verify -->
      <div class="flex-1">
        <div
          class="bg-[#EBF5FF] p-8 rounded-2xl border border-[#B0D7F8] flex flex-col h-full shadow-lg"
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

      <!-- Keypad -->
      <div class="flex-1">
        <div
          class="bg-white p-7 rounded-2xl shadow-lg border border-gray-200 flex flex-col items-center h-full justify-center"
        >
          <div class="relative flex flex-col items-center mb-8">
            <div :class="['flex gap-4', { 'animate-shake': isShaking }]">
              <div
                v-for="i in pinLength"
                :key="i"
                :class="[
                  'w-4 h-4 rounded-full border-2 transition-all',
                  pinBuffer.length >= i
                    ? 'bg-[#03335C] border-[#03335C]'
                    : 'bg-transparent border-gray-400',
                ]"
              ></div>
            </div>

            <p
              v-if="verificationError"
              class="absolute top-[22px] text-red-500 text-sm tracking-tight whitespace-nowrap"
            >
              {{ verificationError }}
            </p>
          </div>

          <div class="grid grid-cols-3 gap-3 w-full">
            <button
              v-for="n in 9"
              :key="n"
              @click="handleKeypad(n.toString())"
              class="h-14 rounded-xl bg-gray-100 text-[#03335C] text-2xl font-bold border border-gray-100 active:bg-gray-200 transition-colors"
            >
              {{ n }}
            </button>
            <div class="h-14"></div>
            <button
              @click="handleKeypad('0')"
              class="h-14 rounded-xl bg-gray-100 text-[#03335C] text-2xl font-bold border border-gray-100 active:bg-gray-200 transition-colors"
            >
              0
            </button>
            <button
              @click="handleBackspace"
              class="h-14 rounded-xl bg-yellow-100/60 text-yellow-700 active:bg-yellow-200/60 flex items-center justify-center transition-colors"
            >
              <BackspaceIcon class="w-7 h-7" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Passcode Updated!"
          message="Your security PIN has been successfully changed."
          :show-secondary-button="false"
          primary-button-text="Done"
          @primary-click="handleModalDone"
        />
      </div>
    </Transition>
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

.modal-backdrop {
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  backdrop-filter: blur(8px);
}

.animate-fadeIn {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}
@keyframes shake {
  10%,
  90% {
    transform: translate3d(-1px, 0, 0);
  }
  20%,
  80% {
    transform: translate3d(2px, 0, 0);
  }
  30%,
  50%,
  70% {
    transform: translate3d(-4px, 0, 0);
  }
  40%,
  60% {
    transform: translate3d(4px, 0, 0);
  }
}
</style>