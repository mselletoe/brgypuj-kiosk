<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { searchResidents, getReportCardInfo, reportLostCard } from "@/api/idService";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";
import {
  BackspaceIcon,
  ExclamationTriangleIcon,
  CalendarDaysIcon,
  UserIcon,
  ChevronDownIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();
const authStore = useAuthStore();

// Phase
const currentPhase = ref("selection"); // 'selection' | 'pin'

// PIN state
const pinBuffer = ref("");
const isSubmitting = ref(false);
const isShaking = ref(false);
const verificationError = ref("");
const pinLength = 4;

// Modals
const showSuccessModal = ref(false);
const showNoRfidModal = ref(false);
const showConfirmModal = ref(false);

// Selection state
const lastNameLetter = ref("");
const firstNameLetter = ref("");
const selectedResident = ref(null);   // full info from getReportCardInfo
const residentList = ref([]);
const isFetching = ref(false);
const isCheckingCard = ref(false);

// Dropdowns
const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);
const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// -------------------------------------------------------
// Fetch residents whenever both letters are set
// -------------------------------------------------------
watch([lastNameLetter, firstNameLetter], async ([last, first]) => {
  if (!last || !first) {
    residentList.value = [];
    selectedResident.value = null;
    return;
  }
  isFetching.value = true;
  try {
    residentList.value = await searchResidents(`${last}, ${first}`);
    selectedResident.value = null;
  } catch {
    residentList.value = [];
  } finally {
    isFetching.value = false;
  }
});

const toggleDropdown = (menu) => {
  showLastNameDropdown.value = menu === "lastName" ? !showLastNameDropdown.value : false;
  showFirstNameDropdown.value = menu === "firstName" ? !showFirstNameDropdown.value : false;
  showResidentDropdown.value = menu === "resident" ? !showResidentDropdown.value : false;
};

const selectLastNameLetter = (letter) => {
  lastNameLetter.value = letter;
  showLastNameDropdown.value = false;
  selectedResident.value = null;
};
const selectFirstNameLetter = (letter) => {
  firstNameLetter.value = letter;
  showFirstNameDropdown.value = false;
  selectedResident.value = null;
};

// On resident pick — immediately fetch card info to check has_rfid
const selectResident = async (r) => {
  showResidentDropdown.value = false;
  isCheckingCard.value = true;
  try {
    const info = await getReportCardInfo(r.resident_id);
    selectedResident.value = info; // { resident_id, first_name, last_name, rfid_uid, has_rfid }
  } catch {
    selectedResident.value = { ...r, has_rfid: false, rfid_uid: null };
  } finally {
    isCheckingCard.value = false;
  }
};

// -------------------------------------------------------
// PIN logic
// -------------------------------------------------------
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

const triggerError = (msg) => {
  isShaking.value = true;
  verificationError.value = msg;
  setTimeout(() => {
    isShaking.value = false;
    pinBuffer.value = "";
  }, 500);
};

// -------------------------------------------------------
// Navigation
// -------------------------------------------------------
const proceedToPin = () => {
  if (!selectedResident.value) return;
  if (!selectedResident.value.has_rfid) {
    showNoRfidModal.value = true;
    return;
  }
  currentPhase.value = "pin";
};

const goBack = () => {
  if (currentPhase.value === "pin") {
    currentPhase.value = "selection";
    pinBuffer.value = "";
    verificationError.value = "";
  } else {
    router.push("/id-services");
  }
};

const handleReset = () => {
  lastNameLetter.value = "";
  firstNameLetter.value = "";
  selectedResident.value = null;
  residentList.value = [];
};

// -------------------------------------------------------
// Submit — show confirm modal first, then call API
// -------------------------------------------------------
const submitReport = () => {
  if (pinBuffer.value.length !== pinLength) return;
  showConfirmModal.value = true;
};

const handleFinalDeactivation = async () => {
  showConfirmModal.value = false;
  isSubmitting.value = true;
  try {
    await reportLostCard({
      resident_id: selectedResident.value.resident_id,
      pin: pinBuffer.value,
      rfid_uid: authStore.rfidUid || null,
    });
    // If logged-in user just reported their own card, log them out
    if (authStore.isRFID && authStore.residentId === selectedResident.value.resident_id) {
      authStore.logout();
    }
    showSuccessModal.value = true;
  } catch (err) {
    const status = err?.response?.status;
    const detail = err?.response?.data?.detail || "Something went wrong. Please try again.";
    if (status === 401) {
      triggerError("Incorrect PIN. Please try again.");
    } else {
      triggerError(detail);
    }
  } finally {
    isSubmitting.value = false;
  }
};

const handleModalDone = () => router.push("/id-services");
</script>

<template>
  <div
    class="flex flex-col w-full h-full bg-white overflow-hidden select-none no-scrollbar"
  >
    <div class="flex flex-col h-full">
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

      <div class="flex-1 flex flex-col justify-center items-center pb-8 pt-2">
        <div
          :class="[
            'w-full max-w-[1050px] relative flex flex-col transition-all duration-500 ease-in-out items-center justify-center',
            currentPhase === 'selection'
              ? 'bg-white rounded-[28px] shadow-[0_4px_15px_rgba(0,0,0,0.1)] border border-gray-100 p-[30px] h-[260px]'
              : '',
          ]"
        >
          <!-- Selection Phase -->
          <div
            v-if="currentPhase === 'selection'"
            class="flex w-full h-full items-center justify-start animate-fadeIn"
          >
            <div class="w-full flex flex-col relative px-2">
              <h2 class="text-[25px] font-bold text-[#03335C] text-left">
                Identify Resident
              </h2>
              <p class="text-gray-500 italic text-xs mb-6 text-left">
                Select the resident record associated with the lost RFID card.
              </p>

              <div class="space-y-4 w-full z-20">
                <div class="flex gap-10 w-full">
                  <!-- Last Name Letter -->
                  <div class="flex flex-1 items-center gap-3">
                    <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                      <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                      <div class="flex flex-col leading-tight">
                        <span class="text-[9px] uppercase font-bold text-gray-400">First Letter of</span>
                        <span class="text-[#03335C] font-black text-sm uppercase tracking-tight">Last Name</span>
                      </div>
                    </div>
                    <div class="flex-1 relative">
                      <button
                        @click="toggleDropdown('lastName')"
                        class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                      >
                        {{ lastNameLetter || "Select" }}
                        <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                      </button>
                      <div
                        v-if="showLastNameDropdown"
                        class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll"
                      >
                        <button
                          v-for="l in alphabet"
                          :key="l"
                          @click="selectLastNameLetter(l)"
                          class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                        >
                          {{ l }}
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- First Name Letter -->
                  <div class="flex flex-1 items-center gap-3">
                    <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                      <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                      <div class="flex flex-col leading-tight">
                        <span class="text-[9px] uppercase font-bold text-gray-400">First Letter of</span>
                        <span class="text-[#03335C] font-black text-sm uppercase tracking-tight">First Name</span>
                      </div>
                    </div>
                    <div class="flex-1 relative">
                      <button
                        @click="toggleDropdown('firstName')"
                        class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                      >
                        {{ firstNameLetter || "Select" }}
                        <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                      </button>
                      <div
                        v-if="showFirstNameDropdown"
                        class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll"
                      >
                        <button
                          v-for="l in alphabet"
                          :key="l"
                          @click="selectFirstNameLetter(l)"
                          class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                        >
                          {{ l }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Resident Dropdown -->
                <div class="flex items-center gap-3 w-full">
                  <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                    <UserIcon class="w-5 h-5 text-[#03335C]" />
                    <span class="text-[#03335C] font-bold text-[11px] uppercase tracking-tight">Resident Name</span>
                  </div>
                  <div class="flex-1 relative">
                    <button
                      @click="toggleDropdown('resident')"
                      :disabled="!lastNameLetter || !firstNameLetter || isFetching || isCheckingCard"
                      class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors disabled:opacity-50 disabled:bg-gray-50"
                    >
                      <span v-if="isFetching || isCheckingCard" class="text-gray-400 text-sm italic">Loading...</span>
                      <span v-else-if="selectedResident" class="truncate text-[#03335C]">
                        {{ selectedResident.last_name }}, {{ selectedResident.first_name }}
                      </span>
                      <span v-else class="text-gray-400 truncate opacity-60">{{
                        !lastNameLetter || !firstNameLetter ? "Select initials first..." : "Select Resident..."
                      }}</span>
                      <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                    </button>
                    <div
                      v-if="showResidentDropdown"
                      class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-[150px] overflow-y-auto custom-scroll"
                    >
                      <div
                        v-if="residentList.length === 0"
                        class="p-3 text-center text-gray-400 text-sm"
                      >
                        No records found
                      </div>
                      <button
                        v-for="r in residentList"
                        :key="r.resident_id"
                        @click="selectResident(r)"
                        class="w-full text-left py-2 px-4 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-base border-b border-gray-50 last:border-0"
                      >
                        {{ r.last_name }}, {{ r.first_name }}
                        <span v-if="r.middle_name">{{ r.middle_name }}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- PIN Phase -->
          <div
            v-else-if="currentPhase === 'pin'"
            class="flex w-full gap-10 items-stretch justify-center animate-fadeIn mt-4"
          >
            <div class="flex-1 max-w-[450px] flex flex-col">
              <div
                class="bg-red-50 p-8 rounded-3xl border border-red-100 flex flex-col h-full shadow-sm"
              >
                <div class="flex-1">
                  <ExclamationTriangleIcon class="w-12 h-12 text-red-600 mb-4" />
                  <h2 class="text-3xl font-bold text-[#03335C] mb-2">Critical Action</h2>
                  <p class="text-gray-600 text-base leading-snug mb-4">
                    Reporting the card for
                    <span class="font-bold text-[#03335C]">
                      {{ selectedResident?.first_name }} {{ selectedResident?.last_name }}
                    </span>
                    will
                    <span class="font-bold text-red-600 uppercase">permanently disable</span>
                    its RFID functions.
                  </p>
                  <p class="text-gray-500 text-sm leading-snug">
                    Enter security PIN to authorize this block.
                  </p>
                </div>

                <Button
                  @click="submitReport"
                  :disabled="pinBuffer.length !== pinLength || isSubmitting"
                  class="w-full py-5 text-xl font-bold shadow-md !bg-red-600 hover:!bg-red-700 disabled:!bg-gray-200 mt-10"
                >
                  {{ isSubmitting ? "Processing..." : "Confirm & Block" }}
                </Button>
              </div>
            </div>

            <div class="flex-1 max-w-[400px] flex flex-col">
              <div
                class="bg-white p-7 rounded-3xl shadow-[0_5px_15px_-5px_rgba(0,0,0,0.08)] border border-gray-100 flex flex-col items-center h-full justify-center"
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
                          : 'bg-transparent border-gray-300',
                      ]"
                    ></div>
                  </div>
                  <p
                    v-if="verificationError"
                    class="absolute top-[22px] text-red-500 text-sm tracking-tight whitespace-nowrap font-normal"
                  >
                    {{ verificationError }}
                  </p>
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
      </div>

      <!-- Bottom bar (selection phase only) -->
      <div
        v-if="currentPhase === 'selection'"
        class="flex gap-6 mt-4 w-full max-w-[1050px] mx-auto justify-between items-center flex-shrink-0 px-4"
      >
        <Button
          variant="outline"
          size="md"
          @click="handleReset"
          :disabled="!lastNameLetter && !firstNameLetter && !selectedResident"
        >Reset Selection</Button>
        <Button
          :variant="selectedResident ? 'secondary' : 'disabled'"
          size="md"
          :disabled="!selectedResident || isCheckingCard"
          @click="proceedToPin"
        >
          {{
            isCheckingCard
              ? "Checking..."
              : selectedResident && !selectedResident.has_rfid
                ? "No RFID Linked"
                : "Next: Verify PIN"
          }}
        </Button>
      </div>
    </div>

    <!-- Confirm Deactivation Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showConfirmModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Disable RFID Card?"
          message="Are you sure you want to permanently disable this card? This action cannot be undone."
          primary-button-text="Yes, Block Card"
          secondary-button-text="Cancel"
          :show-secondary-button="true"
          @primary-click="handleFinalDeactivation"
          @secondary-click="showConfirmModal = false"
        />
      </div>
    </Transition>

    <!-- Success Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Card Deactivated"
          message="The RFID card has been successfully unlinked and blocked for security purposes."
          :show-secondary-button="false"
          primary-button-text="Done"
          @primary-click="handleModalDone"
        />
      </div>
    </Transition>

    <!-- No RFID Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showNoRfidModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="No RFID Card Found"
          message="This resident does not have an active RFID card linked to their account. There is nothing to deactivate."
          :show-secondary-button="false"
          primary-button-text="Close"
          @primary-click="showNoRfidModal = false"
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
.custom-scroll::-webkit-scrollbar {
  width: 6px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background-color: #bde0ef;
  border-radius: 20px;
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
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
.animate-shake {
  animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>