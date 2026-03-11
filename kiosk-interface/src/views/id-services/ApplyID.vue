<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Modal from "@/components/shared/Modal.vue";
import Button from "@/components/shared/Button.vue";
import { searchResidents, verifyBirthdate, applyForID, getIDApplicationFields, generateBrgyID, checkIDRequirements } from "@/api/idService";
import { getResidentAutofillData } from "@/api/residentService";
import {
  CalendarDaysIcon,
  UserIcon,
  ChevronDownIcon,
  CameraIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  InformationCircleIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();
const authStore = useAuthStore();

// State & Phases
const currentPhase = ref("selection"); // 'selection' | 'details' | 'camera'

// Details Phase State
const idFields = ref([]);
const detailsForm = ref({});
const detailsErrors = ref({});
const useManualEntry = ref(false);
const isFetchingAutofill = ref(false);
const brgyIdNumber = ref("");

// Maps fixed placeholder names → autofill response keys from getResidentAutofillData
const AUTOFILL_MAP = {
  last_name:      "last_name",
  first_name:     "first_name",
  middle_name:    "middle_name",
  birthdate:      "birthdate",
  address:        "full_address",
  phone_number: "phone_number",
};

// Fetch the admin-configured ID fields on mount
async function loadIDFields() {
  try {
    const { data } = await getIDApplicationFields();
    idFields.value = data;
  } catch {
    idFields.value = [];
  }
}

function buildEmptyForm() {
  const form = {};
  const errors = {};
  for (const field of idFields.value) {
    form[field.name] = "";
    errors[field.name] = "";
  }
  detailsForm.value = form;
  detailsErrors.value = errors;
}

function applyAutofill(autofill) {
  for (const field of idFields.value) {
    const autofillKey = AUTOFILL_MAP[field.name];
    if (autofillKey) {
      let val = autofill[autofillKey] || "";
      // Normalize date to YYYY-MM-DD for <input type="date">
      if (field.type === "date" && val) {
        // Convert MM/DD/YYYY → YYYY-MM-DD
        const parts = val.split("/");
        if (parts.length === 3) {
          val = `${parts[2]}-${parts[0]}-${parts[1]}`;
        } else {
          val = String(val).slice(0, 10); // fallback for ISO format
        }
      }
      detailsForm.value[field.name] = val;
    }
  }
}

function validateDetails() {
  let valid = true;
  for (const field of idFields.value) {
    detailsErrors.value[field.name] = "";
    if (field.required && !detailsForm.value[field.name]) {
      detailsErrors.value[field.name] = "This field is required.";
      valid = false;
    }
  }
  return valid;
}
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const showErrorModal = ref(false);
const showPendingModal = ref(false);
const showVerificationModal = ref(false);
const referenceId = ref("");

// Requirements Modal State
const showRequirementsModal = ref(false);
const requirementsChecks = ref([]);
const isEligible = ref(true);
const isCheckingRequirements = ref(false);

// Selection State
const lastNameLetter = ref("");
const firstNameLetter = ref("");
const selectedResident = ref(null);
const residentList = ref([]);
const isFetching = ref(false);

// Verification State
const verifyMonth = ref("");
const verifyDay = ref("");
const verifyYear = ref("");
const verificationError = ref("");
const isVerifying = ref(false);

const months = [
  { name: "January", value: "01" },
  { name: "February", value: "02" },
  { name: "March", value: "03" },
  { name: "April", value: "04" },
  { name: "May", value: "05" },
  { name: "June", value: "06" },
  { name: "July", value: "07" },
  { name: "August", value: "08" },
  { name: "September", value: "09" },
  { name: "October", value: "10" },
  { name: "November", value: "11" },
  { name: "December", value: "12" },
];

const days = Array.from({ length: 31 }, (_, i) =>
  (i + 1).toString().padStart(2, "0"),
);

const currentYear = new Date().getFullYear();
const years = Array.from({ length: currentYear - 1899 }, (_, i) =>
  (currentYear - i).toString(),
);

// Dropdown Visibility State
const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);
const showMonthDropdown = ref(false);
const showDayDropdown = ref(false);
const showYearDropdown = ref(false);

const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// -------------------------------------------------------
// Fetch residents from API whenever both letters are set
// -------------------------------------------------------
watch([lastNameLetter, firstNameLetter], async ([last, first]) => {
  if (!last || !first) {
    residentList.value = [];
    selectedResident.value = null;
    return;
  }
  isFetching.value = true;
  try {
    const { data } = await searchResidents(`${last}, ${first}`);
    residentList.value = data;
    selectedResident.value = null;
  } catch {
    residentList.value = [];
  } finally {
    isFetching.value = false;
  }
});

const toggleDropdown = (menu) => {
  showLastNameDropdown.value =
    menu === "lastName" ? !showLastNameDropdown.value : false;
  showFirstNameDropdown.value =
    menu === "firstName" ? !showFirstNameDropdown.value : false;
  showResidentDropdown.value =
    menu === "resident" ? !showResidentDropdown.value : false;
  showMonthDropdown.value = menu === "month" ? !showMonthDropdown.value : false;
  showDayDropdown.value = menu === "day" ? !showDayDropdown.value : false;
  showYearDropdown.value = menu === "year" ? !showYearDropdown.value : false;
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
    if (videoRef.value) videoRef.value.srcObject = stream.value;
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

  if (selectedResident.value.has_rfid) {
    showErrorModal.value = true;
    return;
  }

  if (selectedResident.value.has_pending) {
    showPendingModal.value = true;
    return;
  }

  verifyMonth.value = "";
  verifyDay.value = "";
  verifyYear.value = "";
  verificationError.value = "";
  showVerificationModal.value = true;
};

const handleVerification = async () => {
  if (!verifyMonth.value || !verifyDay.value || !verifyYear.value) {
    verificationError.value = "Please complete the date.";
    return;
  }

  const inputDate = `${verifyYear.value}-${verifyMonth.value}-${verifyDay.value}`;
  isVerifying.value = true;
  verificationError.value = "";

  try {
    const { data: result } = await verifyBirthdate({
      resident_id: selectedResident.value.resident_id,
      birthdate: inputDate,
    });

    if (result.verified) {
      showVerificationModal.value = false;
      // Check requirements before proceeding
      isCheckingRequirements.value = true;
      try {
        const { data: reqResult } = await checkIDRequirements(selectedResident.value.resident_id);
        requirementsChecks.value = reqResult.checks;
        isEligible.value = reqResult.eligible;
      } catch {
        requirementsChecks.value = [];
        isEligible.value = true;
      } finally {
        isCheckingRequirements.value = false;
      }
      showRequirementsModal.value = true;
    } else {
      verificationError.value = "Birthdate does not match our records.";
    }
  } catch {
    verificationError.value = "Verification failed. Please try again.";
  } finally {
    isVerifying.value = false;
  }
};

const proceedFromRequirements = async () => {
  showRequirementsModal.value = false;
  useManualEntry.value = !authStore.rfidUid;
  buildEmptyForm();
  if (authStore.rfidUid && selectedResident.value?.resident_id) {
    isFetchingAutofill.value = true;
    try {
      const { data: autofill } = await getResidentAutofillData(selectedResident.value.resident_id);
      applyAutofill(autofill);
    } catch {
      useManualEntry.value = true;
    } finally {
      isFetchingAutofill.value = false;
    }
  }
  // Generate and reserve the brgy_id_number immediately
  try {
    const { data: idData } = await generateBrgyID();
    brgyIdNumber.value = idData.brgy_id_number;
  } catch {
    brgyIdNumber.value = "";
  }
  currentPhase.value = "details";
};

const proceedToCameraFromDetails = () => {
  if (!validateDetails()) return;
  currentPhase.value = "camera";
  startCamera();
};

const goBack = () => {
  if (isCountingDown.value) return;
  if (currentPhase.value === "camera") {
    stopCamera();
    photoData.value = null;
    currentPhase.value = "details";
  } else if (currentPhase.value === "details") {
    currentPhase.value = "selection";
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

const submitApplication = async () => {
  if (!selectedResident.value || !photoData.value) return;

  isSubmitting.value = true;
  stopCamera();

  try {
    const { data: result } = await applyForID({
      resident_id: authStore.residentId || null,
      applicant_resident_id: selectedResident.value.resident_id,
      rfid_uid: authStore.rfidUid || null,
      photo: photoData.value,
      use_manual_data: useManualEntry.value,
      field_values: { brgy_id_number: brgyIdNumber.value, ...detailsForm.value },
    });

    referenceId.value = result.transaction_no;
    showSuccessModal.value = true;
  } catch (err) {
    const msg =
      err?.response?.data?.detail || "Submission failed. Please try again.";
    console.error("ID application failed:", msg);
    startCamera();
  } finally {
    isSubmitting.value = false;
  }
};

const handleModalDone = () => router.push("/id-services");

onMounted(loadIDFields);

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
  selectedResident.value = null;
};

const selectResident = (resident) => {
  selectedResident.value = resident;
  showResidentDropdown.value = false;
};

const selectMonth = (m) => {
  verifyMonth.value = m.value;
  showMonthDropdown.value = false;
};
const selectDay = (d) => {
  verifyDay.value = d;
  showDayDropdown.value = false;
};
const selectYear = (y) => {
  verifyYear.value = y;
  showYearDropdown.value = false;
};
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
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

    <!-- Main -->
    <div class="flex-1 mb-4 min-h-0">
      <div
        :class="currentPhase === 'details' ? 'h-full' : ''"
        class="w-full bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex flex-col transition-all duration-500 ease-in-out"
      >
        <!-- Resident Selection Form-->
        <div
          v-if="currentPhase === 'selection'"
          class="flex w-full h-full items-center justify-start animate-fadeIn"
        >
          <div class="w-full flex flex-col relative px-2">
            <h2 class="text-[25px] font-bold text-[#03335C] text-left">
              Resident Selection
            </h2>
            <p class="text-gray-500 italic text-xs mb-6 text-left">
              Select the Resident to be linked to the new RFID card
            </p>

            <div class="space-y-4 w-full">
              <div class="flex gap-10 w-full">
                <!-- Last Name Letter -->
                <div class="flex flex-1 items-center gap-3">
                  <div
                    class="flex items-center gap-2 flex-shrink-0 min-w-[140px]"
                  >
                    <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                    <div class="flex flex-col leading-tight">
                      <span class="text-[9px] uppercase font-bold text-gray-400"
                        >First Letter of</span
                      >
                      <span
                        class="text-[#03335C] font-black text-sm uppercase tracking-tight"
                        >Surname</span
                      >
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
                  <div
                    class="flex items-center gap-2 flex-shrink-0 min-w-[140px]"
                  >
                    <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                    <div class="flex flex-col leading-tight">
                      <span class="text-[9px] uppercase font-bold text-gray-400"
                        >First Letter of</span
                      >
                      <span
                        class="text-[#03335C] font-black text-sm uppercase tracking-tight"
                        >First Name</span
                      >
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

              <!-- Resident Name Dropdown -->
              <div class="flex items-center gap-3 w-full">
                <div
                  class="flex items-center gap-2 flex-shrink-0 min-w-[140px]"
                >
                  <UserIcon class="w-5 h-5 text-[#03335C]" />
                  <span
                    class="text-[#03335C] font-bold text-[11px] uppercase tracking-tight"
                    >Resident Name</span
                  >
                </div>
                <div class="flex-1 relative">
                  <button
                    @click="toggleDropdown('resident')"
                    :disabled="
                      !lastNameLetter || !firstNameLetter || isFetching
                    "
                    class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors disabled:opacity-50 disabled:bg-gray-50"
                  >
                    <span v-if="isFetching" class="text-gray-400 text-sm italic"
                      >Loading...</span
                    >
                    <span
                      v-else-if="selectedResident"
                      class="truncate text-[#03335C]"
                      >{{ selectedResident.last_name }},
                      {{ selectedResident.first_name }}
                      <span v-if="selectedResident.middle_name">{{
                        selectedResident.middle_name
                      }}</span>
                    </span>
                    <span v-else class="text-gray-400 truncate opacity-60">{{
                      !lastNameLetter || !firstNameLetter
                        ? "Select initials first..."
                        : "Select Resident..."
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

        <!-- Details Phase -->
        <div
          v-else-if="currentPhase === 'details'"
          class="flex w-full h-full items-start justify-start animate-fadeIn overflow-hidden"
        >
          <div class="w-full h-full flex flex-col px-2">
            <h2 class="text-2xl font-bold text-[#03335C] flex items-center gap-2 mb-1 flex-shrink-0">
              <DocumentTextIcon class="w-8 h-8" />
              ID Card Details
            </h2>
            <p class="text-gray-500 italic text-xs mb-6 text-left flex-shrink-0">
              Review and confirm the information to be printed on the ID card.
            </p>

            <div class="flex-1 overflow-y-auto pr-1 min-h-0 custom-scroll px-1 pt-1">
              <div v-if="isFetchingAutofill" class="flex items-center gap-3 py-6 text-[#03335C]">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#03335C]"></div>
                <span class="text-sm font-medium">Loading resident data...</span>
              </div>

              <template v-else>
                <!-- Manual override toggle (RFID users only) -->
                <div v-if="authStore.rfidUid" class="mb-5 flex items-center gap-3">
                  <input
                    id="manualEntry"
                    type="checkbox"
                    v-model="useManualEntry"
                    class="h-5 w-5 text-[#013C6D]"
                  />
                  <label for="manualEntry" class="text-sm text-gray-700 italic cursor-pointer select-none">
                    Enter information manually instead of using database records
                  </label>
                </div>

                <div v-if="idFields.length === 0" class="text-sm text-gray-400 italic py-4">
                  No fields have been configured by the admin for this form.
                </div>

                <div v-else class="grid grid-cols-2 gap-x-6 gap-y-4 pb-2">
                  <div
                    v-for="field in idFields"
                    :key="field.id || field.name"
                    :class="field.type === 'textarea' ? 'col-span-2' : 'col-span-1'"
                    class="flex flex-col"
                  >
                    <label class="block text-base font-bold text-[#003A6B] mb-2">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-600">*</span>
                    </label>

                    <textarea
                      v-if="field.type === 'textarea'"
                      v-model="detailsForm[field.name]"
                      :disabled="!useManualEntry && !!AUTOFILL_MAP[field.name]"
                      :placeholder="field.label"
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D] disabled:bg-gray-50 disabled:text-gray-400 resize-none"
                      rows="2"
                    ></textarea>

                    <input
                      v-else
                      v-model="detailsForm[field.name]"
                      :disabled="!useManualEntry && !!AUTOFILL_MAP[field.name]"
                      :type="field.type === 'date' ? 'date' : field.type === 'number' ? 'number' : 'text'"
                      :placeholder="field.label"
                      class="w-full h-[48px] px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D] disabled:bg-gray-50 disabled:text-gray-400"
                    />

                    <p v-if="detailsErrors[field.name]" class="text-red-500 text-xs italic mt-1">
                      {{ detailsErrors[field.name] }}
                    </p>
                  </div>
                </div>
              </template>
            </div>

          </div>
        </div>

        <!-- Camera Phase -->
        <div
          v-else-if="currentPhase === 'camera'"
          class="flex w-full h-[340px] gap-20 items-center justify-center animate-fadeIn"
        >
          <div class="flex-shrink-0 h-full relative">
            <div
              class="h-full aspect-square bg-black rounded-3xl overflow-hidden relative flex items-center justify-center"
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
            class="w-[380px] flex flex-col justify-center h-full flex-shrink-0"
          >
            <div class="flex-1 flex flex-col justify-center">
              <h2 class="text-3xl font-bold text-[#03335C] mb-1">
                Capture ID Photo
              </h2>
              <p class="text-gray-500 italic text-sm mb-4">
                Take a clear photo for your new RFID Card.
              </p>
              <div class="bg-[#EAF6FB] rounded-2xl p-6 border border-[#BDE0EF] flex flex-col gap-3">
                <div>
                  <p
                    class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1"
                  >
                    Applying For:
                  </p>
                  <p class="font-black text-[#03335C] text-xl truncate">
                    {{ selectedResident?.first_name }}
                    {{ selectedResident?.last_name }}
                  </p>
                </div>
                <div class="border-t border-[#BDE0EF] pt-3">
                  <p
                    class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1"
                  >
                    Barangay ID No.:
                  </p>
                  <p v-if="brgyIdNumber" class="font-black text-[#03335C] text-xl tracking-widest font-mono">
                    {{ brgyIdNumber }}
                  </p>
                  <p v-else class="text-gray-400 text-sm italic">Generating...</p>
                </div>
              </div>
            </div>
            <div class="flex gap-3 mt-4">
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
                  >Retake</Button
                >
                <Button
                  :variant="isSubmitting ? 'disabled' : 'secondary'"
                  size="md"
                  class="w-full justify-center text-lg py-4"
                  :disabled="isSubmitting"
                  @click="submitApplication"
                  >{{
                    isSubmitting ? "Processing..." : "Submit"
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
      class="flex gap-6 mt-6 justify-between items-center flex-shrink-0"
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

    <div
      v-else-if="currentPhase === 'details'"
      class="flex gap-6 mt-6 justify-between items-center flex-shrink-0"
    >
      <Button variant="outline" size="md" @click="currentPhase = 'selection'">Back</Button>
      <Button
        variant="secondary"
        size="md"
        @click="proceedToCameraFromDetails"
        >Next: Take Photo</Button
      >
    </div>

    <!-- Requirements Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showRequirementsModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <div class="bg-white rounded-[28px] p-10 max-w-[560px] w-full shadow-2xl relative">
          <!-- Loading state -->
          <div v-if="isCheckingRequirements" class="flex flex-col items-center py-8 gap-4">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#03335C]"></div>
            <p class="text-[#03335C] font-medium">Checking requirements...</p>
          </div>

          <template v-else>
            <h2 class="text-2xl font-bold text-[#03335C] mb-1">Application Requirements</h2>
            <p class="text-gray-500 text-sm mb-6">
              The following requirements were checked for
              <strong>{{ selectedResident?.first_name }} {{ selectedResident?.last_name }}</strong>.
            </p>

            <!-- No requirements configured -->
            <div v-if="requirementsChecks.length === 0" class="flex items-center gap-3 py-4 px-4 bg-blue-50 rounded-2xl mb-6">
              <InformationCircleIcon class="w-6 h-6 text-blue-500 flex-shrink-0" />
              <p class="text-sm text-blue-700">No specific requirements have been configured for this ID application. You may proceed.</p>
            </div>

            <!-- Requirements list -->
            <div v-else class="flex flex-col gap-3 mb-6 max-h-64 overflow-y-auto custom-scroll pr-1">
              <div
                v-for="check in requirementsChecks"
                :key="check.id"
                class="flex items-start gap-3 p-4 rounded-2xl border"
                :class="{
                  'bg-green-50 border-green-200': check.passed === true,
                  'bg-red-50 border-red-200': check.passed === false,
                  'bg-amber-50 border-amber-200': check.passed === null && check.type === 'system_check',
                  'bg-blue-50 border-blue-200': check.type === 'document',
                }"
              >
                <!-- Icon -->
                <div class="flex-shrink-0 mt-0.5">
                  <CheckCircleIcon v-if="check.passed === true" class="w-5 h-5 text-green-500" />
                  <XCircleIcon v-else-if="check.passed === false" class="w-5 h-5 text-red-500" />
                  <ClockIcon v-else-if="check.passed === null && check.type === 'system_check'" class="w-5 h-5 text-amber-500" />
                  <InformationCircleIcon v-else class="w-5 h-5 text-blue-500" />
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <p class="font-bold text-sm"
                    :class="{
                      'text-green-800': check.passed === true,
                      'text-red-800': check.passed === false,
                      'text-amber-800': check.passed === null && check.type === 'system_check',
                      'text-blue-800': check.type === 'document',
                    }"
                  >{{ check.label }}</p>
                  <p class="text-xs mt-0.5"
                    :class="{
                      'text-green-600': check.passed === true,
                      'text-red-600': check.passed === false,
                      'text-amber-600': check.passed === null && check.type === 'system_check',
                      'text-blue-600': check.type === 'document',
                    }"
                  >{{ check.message }}</p>
                </div>

                <!-- Badge -->
                <span class="flex-shrink-0 text-[10px] font-bold uppercase px-2 py-1 rounded-full"
                  :class="{
                    'bg-green-100 text-green-700': check.passed === true,
                    'bg-red-100 text-red-700': check.passed === false,
                    'bg-amber-100 text-amber-700': check.passed === null && check.type === 'system_check',
                    'bg-blue-100 text-blue-700': check.type === 'document',
                  }"
                >
                  {{ check.passed === true ? 'Passed' : check.passed === false ? 'Failed' : check.type === 'document' ? 'Bring this' : 'Pending' }}
                </span>
              </div>
            </div>

            <!-- Ineligible warning -->
            <div v-if="!isEligible" class="flex items-start gap-3 p-4 bg-red-50 rounded-2xl border border-red-200 mb-6">
              <XCircleIcon class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p class="text-sm text-red-700 font-medium">
                This resident does not meet one or more required criteria. The application cannot be submitted at this time. Please visit the barangay hall for assistance.
              </p>
            </div>

            <div class="flex gap-4 mt-2">
              <Button
                variant="outline"
                class="flex-1"
                @click="showRequirementsModal = false"
              >Cancel</Button>
              <Button
                v-if="isEligible"
                variant="secondary"
                class="flex-1"
                @click="proceedFromRequirements"
              >Proceed to Application</Button>
              <Button
                v-else
                variant="disabled"
                class="flex-1"
                disabled
              >Cannot Proceed</Button>
            </div>
          </template>
        </div>
      </div>
    </Transition>

    <!-- Birthdate Verification Modal -->
    <Transition name="fade-blur">
      <div
        v-if="showVerificationModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <div
          class="bg-white rounded-[28px] p-10 max-w-[500px] w-full shadow-2xl relative"
        >
          <h2 class="text-2xl font-bold text-[#03335C] mb-2">
            Verify Identity
          </h2>
          <p class="text-gray-500 text-sm mb-6">
            Please enter the birthdate for
            <strong
              >{{ selectedResident?.first_name }}
              {{ selectedResident?.last_name }}</strong
            >
            to proceed.
          </p>
          <div class="flex gap-3 mb-4">
            <!-- Month -->
            <div class="flex-1 relative">
              <label
                class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
                >Month</label
              >
              <button
                @click="toggleDropdown('month')"
                class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
              >
                {{
                  months.find((m) => m.value === verifyMonth)?.name || "Select"
                }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div
                v-if="showMonthDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
              >
                <button
                  v-for="m in months"
                  :key="m.value"
                  @click="selectMonth(m)"
                  class="w-full text-left py-2 px-3 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
                >
                  {{ m.name }}
                </button>
              </div>
            </div>
            <!-- Day -->
            <div class="flex-1 relative">
              <label
                class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
                >Day</label
              >
              <button
                @click="toggleDropdown('day')"
                class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
              >
                {{ verifyDay || "DD" }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div
                v-if="showDayDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
              >
                <button
                  v-for="d in days"
                  :key="d"
                  @click="selectDay(d)"
                  class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
                >
                  {{ d }}
                </button>
              </div>
            </div>
            <!-- Year -->
            <div class="flex-1 relative">
              <label
                class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
                >Year</label
              >
              <button
                @click="toggleDropdown('year')"
                class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
              >
                {{ verifyYear || "YYYY" }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div
                v-if="showYearDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
              >
                <button
                  v-for="y in years"
                  :key="y"
                  @click="selectYear(y)"
                  class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
                >
                  {{ y }}
                </button>
              </div>
            </div>
          </div>
          <p
            v-if="verificationError"
            class="text-red-500 text-xs font-bold mb-4 animate-shake"
          >
            {{ verificationError }}
          </p>
          <div class="flex gap-4 mt-8">
            <Button
              variant="outline"
              class="flex-1"
              :disabled="isVerifying"
              @click="showVerificationModal = false"
              >Cancel</Button
            >
            <Button
              :variant="isVerifying ? 'disabled' : 'secondary'"
              class="flex-1"
              :disabled="isVerifying"
              @click="handleVerification"
              >{{ isVerifying ? "Verifying..." : "Verify & Proceed" }}</Button
            >
          </div>
        </div>
      </div>
    </Transition>

    <!-- Success Modal -->
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

    <!-- Error Modal: Active RFID already exists -->
    <Transition name="fade-blur">
      <div
        v-if="showErrorModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Existing RFID Found"
          message="This resident already has an existing RFID number. You cannot request a new card while an existing one is active. Please disable the current card first."
          :show-reference-id="false"
          :show-primary-button="true"
          :show-secondary-button="false"
          primary-button-text="Close"
          @primary-click="showErrorModal = false"
        />
      </div>
    </Transition>

    <!-- Error Modal: Pending ID application already exists -->
    <Transition name="fade-blur">
      <div
        v-if="showPendingModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          title="Application Already Pending"
          message="This resident already has a pending ID application. You cannot submit another request until the current one has been processed. Please check back later or visit the barangay office."
          :show-reference-id="false"
          :show-primary-button="true"
          :show-secondary-button="false"
          primary-button-text="Close"
          @primary-click="showPendingModal = false"
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