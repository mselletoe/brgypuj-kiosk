<script setup>
import { ref, computed, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Modal from "@/components/shared/Modal.vue";
import Button from "@/components/shared/Button.vue";
import {
  CalendarDaysIcon,
  UserIcon,
  ChevronDownIcon,
  CameraIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();

// State & Phases
const currentPhase = ref("selection"); // 'selection' | 'camera'
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const referenceId = ref("");

// Selection State
const lastNameLetter = ref("");
const firstNameLetter = ref("");
const selectedResident = ref(null);

// Dropdown Visibility State
const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);

const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// Mock Database
const mockResidents = [
  {
    id: 1,
    firstName: "Aaron",
    lastName: "Abad",
    address: "Block 5 Lot 2",
    birthdate: "1998-05-12",
    rfid: "N/A",
  },
  {
    id: 2,
    firstName: "Adrian",
    lastName: "Agoncillo",
    address: "Block 12 Lot 1",
    birthdate: "2001-11-03",
    rfid: "N/A",
  },
  {
    id: 3,
    firstName: "Bea",
    lastName: "Alonzo",
    address: "Block 3 Lot 8",
    birthdate: "1995-02-14",
    rfid: "N/A",
  },
  {
    id: 7,
    firstName: "Keanno",
    lastName: "Macatangay",
    address: "Makati Homes 2",
    birthdate: "2003-01-15",
    rfid: "N/A",
  },
];

// Computed Filter
const filteredResidents = computed(() => {
  if (!lastNameLetter.value) return [];
  return mockResidents.filter((r) =>
    r.lastName.startsWith(lastNameLetter.value),
  );
});

// --- DROPDOWN LOGIC ---
const toggleDropdown = (menu) => {
  showLastNameDropdown.value =
    menu === "lastName" ? !showLastNameDropdown.value : false;
  showFirstNameDropdown.value =
    menu === "firstName" ? !showFirstNameDropdown.value : false;
  showResidentDropdown.value =
    menu === "resident" ? !showResidentDropdown.value : false;
};

// --- CAMERA LOGIC ---
const videoRef = ref(null);
const canvasRef = ref(null);
const stream = ref(null);
const photoData = ref(null);

const countdown = ref(0);
const isCountingDown = ref(false);
let countdownInterval = null;

const startCamera = async () => {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ video: true });
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
    }
  } catch (err) {
    console.error("Camera access denied:", err);
  }
};

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach((track) => track.stop());
    stream.value = null;
  }
  if (countdownInterval) clearInterval(countdownInterval);
  isCountingDown.value = false;
};

const startCountdown = () => {
  if (isCountingDown.value) return;
  isCountingDown.value = true;
  countdown.value = 5;
  countdownInterval = setInterval(() => {
    countdown.value -= 1;
    if (countdown.value === 0) {
      clearInterval(countdownInterval);
      isCountingDown.value = false;
      executeCapture();
    }
  }, 1000);
};

const executeCapture = () => {
  if (!videoRef.value || !canvasRef.value) return;
  const video = videoRef.value;
  const canvas = canvasRef.value;
  const size = Math.min(video.videoWidth, video.videoHeight);
  const startX = (video.videoWidth - size) / 2;
  const startY = (video.videoHeight - size) / 2;
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, startX, startY, size, size, 0, 0, size, size);
  photoData.value = canvas.toDataURL("image/png");
};

const retakePhoto = () => {
  photoData.value = null;
};

// --- NAVIGATION & ACTIONS ---
const proceedToCamera = () => {
  if (!selectedResident.value) return;
  currentPhase.value = "camera";
  startCamera();
};

const backToSelection = () => {
  stopCamera();
  photoData.value = null;
  currentPhase.value = "selection";
};

const goBack = () => {
  if (isCountingDown.value) return;
  if (currentPhase.value === "camera") {
    backToSelection();
  } else {
    router.push("/id-services");
  }
};

const handleReset = () => {
  lastNameLetter.value = "";
  firstNameLetter.value = "";
  selectedResident.value = null;
  showLastNameDropdown.value = false;
  showFirstNameDropdown.value = false;
  showResidentDropdown.value = false;
};

const submitApplication = () => {
  if (!selectedResident.value || !photoData.value) return;
  isSubmitting.value = true;
  stopCamera();
  setTimeout(() => {
    isSubmitting.value = false;
    referenceId.value = `APP-${Math.floor(100000 + Math.random() * 900000)}`;
    showSuccessModal.value = true;
  }, 1500);
};

const handleModalDone = () => router.push("/id-services");

onUnmounted(() => {
  stopCamera();
});

const selectLastNameLetter = (letter) => {
  lastNameLetter.value = letter;
  showLastNameDropdown.value = false;
  selectedResident.value = null;
};
const selectFirstNameLetter = (letter) => {
  firstNameLetter.value = letter;
  showFirstNameDropdown.value = false;
};
const selectResident = (resident) => {
  selectedResident.value = resident;
  showResidentDropdown.value = false;
};
</script>

<template>
  <div
    class="flex flex-col w-full h-full bg-white overflow-hidden select-none no-scrollbar"
  >
    <div class="flex flex-col h-full">
      <div class="flex items-center mb-4 gap-7 flex-shrink-0">
        <ArrowBackButton @click="goBack" :disabled="isCountingDown" />
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Apply for RFID
          </h1>
          <p class="text-[#03335C] -mt-2">
            Select a resident record to begin the application.
          </p>
        </div>
      </div>

      <div class="flex-1 flex flex-col justify-center items-center pb-8">
        <div
          :class="[
            'w-full bg-white rounded-[28px] shadow-[0_4px_15px_rgba(0,0,0,0.1)] border border-gray-100 p-[25px] relative flex flex-col transition-all duration-500 ease-in-out',
            currentPhase === 'selection'
              ? 'h-[290px] max-w-[1050px]'
              : 'h-[380px] max-w-[780px]',
          ]"
        >
          <div
            v-if="currentPhase === 'selection'"
            class="flex w-full h-full gap-10 items-center"
          >
            <div class="flex-1 flex flex-col relative w-full h-full">
              <h2 class="text-2xl font-bold text-[#03335C] mb-0.5">
                Resident Selection
              </h2>
              <p class="text-gray-500 italic text-xs mb-4">
                Select the Resident to be linked to the new RFID card
              </p>
              <div class="space-y-4 w-full z-20">
                <div class="flex gap-6 w-full">
                  <div class="flex-1 relative">
                    <div class="flex items-center gap-2 mb-1.5">
                      <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                      <span
                        class="text-[#03335C] font-medium text-[11px] uppercase tracking-wider"
                        >First letter of
                        <span class="font-bold">LAST NAME</span></span
                      >
                    </div>
                    <div class="relative">
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
                  <div class="flex-1 relative">
                    <div class="flex items-center gap-2 mb-1.5">
                      <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                      <span
                        class="text-[#03335C] font-medium text-[11px] uppercase tracking-wider"
                        >First letter of
                        <span class="font-bold">FIRST NAME</span></span
                      >
                    </div>
                    <div class="relative">
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
                <div class="relative">
                  <div class="flex items-center gap-2 mb-1.5">
                    <UserIcon class="w-5 h-5 text-[#03335C]" />
                    <span class="text-[#03335C] font-bold text-sm tracking-wide"
                      >Select Resident</span
                    >
                  </div>
                  <button
                    @click="toggleDropdown('resident')"
                    class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                    :disabled="!lastNameLetter"
                  >
                    <span
                      v-if="selectedResident"
                      class="truncate text-[#03335C]"
                      >{{ selectedResident.lastName }},
                      {{ selectedResident.firstName }}</span
                    >
                    <span v-else class="text-gray-400 truncate opacity-60"
                      >Select Resident...</span
                    >
                    <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                  </button>
                  <div
                    v-if="showResidentDropdown && lastNameLetter"
                    class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-[220px] overflow-y-auto custom-scroll"
                  >
                    <button
                      v-for="r in filteredResidents"
                      :key="r.id"
                      @click="selectResident(r)"
                      class="w-full text-left py-2 px-3 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm border-b border-gray-50 last:border-0"
                    >
                      {{ r.lastName }}, {{ r.firstName }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="w-[340px] flex flex-col h-full">
              <div
                class="bg-[#EAF6FB] rounded-2xl p-6 border border-[#BDE0EF] h-[215px] flex flex-col justify-center"
              >
                <h3 class="text-2xl font-bold text-[#03335C] text-center mb-1">
                  Resident Details
                </h3>
                <p
                  class="text-center text-[#03335C] text-xs italic opacity-70 mb-5"
                >
                  Check details before proceeding
                </p>
                <div class="space-y-3 text-[#03335C]">
                  <div class="flex items-center">
                    <span class="w-28 font-bold text-sm">RFID No.:</span
                    ><span class="font-medium text-sm">{{
                      selectedResident?.rfid || "---"
                    }}</span>
                  </div>
                  <div class="flex items-center">
                    <span class="w-28 font-bold text-sm">Name:</span
                    ><span class="font-medium text-sm truncate">{{
                      selectedResident
                        ? `${selectedResident.firstName} ${selectedResident.lastName}`
                        : "---"
                    }}</span>
                  </div>
                  <div class="flex items-center">
                    <span class="w-28 font-bold text-sm">Address:</span
                    ><span class="font-medium text-sm truncate">{{
                      selectedResident?.address || "---"
                    }}</span>
                  </div>
                  <div class="flex items-center">
                    <span class="w-28 font-bold text-sm">Birthdate:</span
                    ><span class="font-medium text-sm">{{
                      selectedResident?.birthdate || "---"
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-else-if="currentPhase === 'camera'"
            class="flex w-full h-full gap-8 items-center justify-center animate-fadeIn"
          >
            <div class="flex-1 flex justify-start items-center h-full relative">
              <div
                class="h-full aspect-square bg-black rounded-3xl overflow-hidden relative border-[6px] border-gray-100 shadow-[inset_0_4px_20px_rgba(0,0,0,0.5)] flex items-center justify-center flex-shrink-0"
              >
                <video
                  v-show="!photoData"
                  ref="videoRef"
                  autoplay
                  playsinline
                  class="w-full h-full object-cover transform scale-x-[-1]"
                ></video>
                <img
                  v-show="photoData"
                  :src="photoData"
                  alt="Captured ID"
                  class="w-full h-full object-cover transform scale-x-[-1]"
                />
                <canvas ref="canvasRef" class="hidden"></canvas>
                <div
                  v-if="!photoData"
                  class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
                >
                  <template v-if="isCountingDown">
                    <span
                      class="text-[80px] font-black text-white drop-shadow-[0_4px_10px_rgba(0,0,0,0.8)] leading-none"
                      >{{ countdown }}</span
                    >
                    <div
                      class="bg-black/60 text-white px-5 py-1.5 rounded-full text-sm tracking-widest uppercase font-bold mt-3 animate-pulse backdrop-blur-sm"
                    >
                      Look at the camera!
                    </div>
                  </template>
                  <div
                    v-else
                    class="absolute bottom-6 bg-black/60 backdrop-blur-md text-white px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase"
                  >
                    Align face in center
                  </div>
                </div>
              </div>
            </div>
            <div
              class="w-[340px] flex flex-col justify-center h-full flex-shrink-0"
            >
              <div class="flex-1 flex flex-col justify-center">
                <h2 class="text-3xl font-bold text-[#03335C] mb-1">
                  Capture ID Photo
                </h2>
                <p class="text-gray-500 italic text-sm mb-6">
                  Take a clear photo for your new RFID Card.
                </p>
                <div
                  class="bg-[#EAF6FB] rounded-2xl p-6 border border-[#BDE0EF]"
                >
                  <p
                    class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-2"
                  >
                    Applying For:
                  </p>
                  <p class="font-black text-[#03335C] text-2xl truncate">
                    {{ selectedResident?.firstName }}
                    {{ selectedResident?.lastName }}
                  </p>
                </div>
              </div>
              <div class="flex flex-col gap-3 mt-4">
                <template v-if="!photoData">
                  <Button
                    :variant="isCountingDown ? 'disabled' : 'primary'"
                    size="md"
                    class="w-full justify-center text-lg py-4"
                    :disabled="isCountingDown"
                    @click="startCountdown"
                  >
                    <span class="flex items-center justify-center gap-2 w-full"
                      ><CameraIcon v-if="!isCountingDown" class="w-6 h-6" />{{
                        isCountingDown ? "Get Ready..." : "Capture Photo"
                      }}</span
                    >
                  </Button>
                </template>
                <template v-else>
                  <Button
                    variant="outline"
                    size="md"
                    class="w-full justify-center text-lg py-3"
                    @click="retakePhoto"
                    :disabled="isSubmitting"
                    >Retake Photo</Button
                  >
                  <Button
                    :variant="isSubmitting ? 'disabled' : 'secondary'"
                    size="md"
                    class="w-full justify-center text-lg py-4"
                    :disabled="isSubmitting"
                    @click="submitApplication"
                    >{{
                      isSubmitting ? "Processing..." : "Submit Application"
                    }}</Button
                  >
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="currentPhase === 'selection'"
        class="flex gap-6 mt-4 w-full max-w-[1050px] mx-auto justify-between items-center flex-shrink-0 px-4"
      >
        <Button
          variant="outline"
          size="md"
          @click="handleReset"
          :disabled="!lastNameLetter && !firstNameLetter && !selectedResident"
          >Reset Selection</Button
        >
        <Button
          :variant="selectedResident ? 'secondary' : 'disabled'"
          size="md"
          :disabled="!selectedResident"
          @click="proceedToCamera"
          >Next: Take Photo</Button
        >
      </div>
    </div>

    <Transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Application Received!"
          message="Your application and photo have been logged. Please proceed to Window 2 and present your Reference ID to claim your card."
          :reference-id="referenceId"
          :show-reference-id="true"
          :show-primary-button="true"
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

/* FADE & BLUR TRANSITION */
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
</style>
