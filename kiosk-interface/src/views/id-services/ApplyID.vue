<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useI18n } from "vue-i18n";
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Modal from "@/components/shared/Modal.vue";
import Button from "@/components/shared/Button.vue";
import VirtualKeyboard from "@/components/shared/Keyboard.vue";
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
const { t } = useI18n();

// State & Phases
const currentPhase = ref("selection"); // 'selection' | 'details' | 'camera'

// Details Phase State
const idFields = ref([]);
const detailsForm = ref({});
const detailsErrors = ref({});
const useManualEntry = ref(false);
const isFetchingAutofill = ref(false);
const brgyIdNumber = ref("");

// Maps fixed placeholder names to autofill response keys
const AUTOFILL_MAP = {
  last_name: "last_name",
  first_name: "first_name",
  middle_name: "middle_name",
  birthdate: "birthdate",
  address: "full_address",
  phone_number: "phone_number",
};

// -------------------------------------------------------
// Keyboard State — mirrors FeedbackComments.vue exactly
// -------------------------------------------------------
const showKeyboard = ref(false);
const activeFieldName = ref(null);

const focusField = (fieldName) => {
  activeFieldName.value = fieldName;
  showKeyboard.value = true;
  nextTick(() => {
    const el = document.getElementById(`field-${fieldName}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  });
};

const handleKeyPress = (char) => {
  if (!activeFieldName.value) return;
  detailsForm.value[activeFieldName.value] = (detailsForm.value[activeFieldName.value] ?? '') + char;
};

const handleDelete = () => {
  if (!activeFieldName.value) return;
  const val = detailsForm.value[activeFieldName.value] ?? '';
  detailsForm.value[activeFieldName.value] = val.slice(0, -1);
};

const handleEnter = () => {
  // Advance to the next editable field, or close keyboard if at end
  const editableFields = idFields.value.filter(
    (f) => f.type !== 'date' && (useManualEntry.value || !AUTOFILL_MAP[f.name])
  );
  const idx = editableFields.findIndex((f) => f.name === activeFieldName.value);
  if (idx !== -1 && idx < editableFields.length - 1) {
    const nextField = editableFields[idx + 1];
    activeFieldName.value = nextField.name;
    nextTick(() => {
      const el = document.getElementById(`field-${nextField.name}`);
      if (el) {
        el.focus();
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  } else {
    showKeyboard.value = false;
    activeFieldName.value = null;
  }
};

const handleHideKeyboard = () => {
  showKeyboard.value = false;
  activeFieldName.value = null;
};

// Hide keyboard when leaving the details phase
watch(currentPhase, (phase) => {
  if (phase !== 'details') {
    showKeyboard.value = false;
    activeFieldName.value = null;
  }
});

// -------------------------------------------------------
// ID Fields
// -------------------------------------------------------
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
      if (field.name === "last_name" && val) val = val.toUpperCase();
      if (field.type === "date" && val) {
        const parts = val.split("/");
        val = parts.length === 3 ? `${parts[2]}-${parts[0]}-${parts[1]}` : String(val).slice(0, 10);
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
  { name: "January", value: "01" }, { name: "February", value: "02" },
  { name: "March", value: "03" },   { name: "April", value: "04" },
  { name: "May", value: "05" },     { name: "June", value: "06" },
  { name: "July", value: "07" },    { name: "August", value: "08" },
  { name: "September", value: "09" },{ name: "October", value: "10" },
  { name: "November", value: "11" }, { name: "December", value: "12" },
];

const days = Array.from({ length: 31 }, (_, i) => (i + 1).toString().padStart(2, "0"));
const currentYear = new Date().getFullYear();
const years = Array.from({ length: currentYear - 1899 }, (_, i) => (currentYear - i).toString());

const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);
const showMonthDropdown = ref(false);
const showDayDropdown = ref(false);
const showYearDropdown = ref(false);

const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

watch([lastNameLetter, firstNameLetter], async ([last, first]) => {
  if (!last || !first) { residentList.value = []; selectedResident.value = null; return; }
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
  showLastNameDropdown.value  = menu === "lastName"  ? !showLastNameDropdown.value  : false;
  showFirstNameDropdown.value = menu === "firstName" ? !showFirstNameDropdown.value : false;
  showResidentDropdown.value  = menu === "resident"  ? !showResidentDropdown.value  : false;
  showMonthDropdown.value     = menu === "month"     ? !showMonthDropdown.value     : false;
  showDayDropdown.value       = menu === "day"       ? !showDayDropdown.value       : false;
  showYearDropdown.value      = menu === "year"      ? !showYearDropdown.value      : false;
};

// --- CAMERA LOGIC (Raspi) ---
const videoRef = ref(null);   // keep for the <img> ref if needed
const canvasRef = ref(null);
const stream = ref(null);
const streamSrc = ref("");    // ADD this
const photoData = ref(null);
const countdown = ref(0);
const isCountingDown = ref(false);
let countdownInterval = null;

const startCamera = async () => {
  if (videoRef.value) {
    videoRef.value.src = "http://" + window.location.hostname + ":8085/?action=stream";
  }
};

const stopCamera = () => {
  if (videoRef.value) { videoRef.value.src = ""; videoRef.value.pause(); }
  if (countdownInterval) clearInterval(countdownInterval);
  isCountingDown.value = false;
};

const executeCapture = async () => {
  try {
    const response = await fetch("/kiosk/camera/snapshot");
    const blob = await response.blob();
    const reader = new FileReader();
    reader.onloadend = () => { photoData.value = reader.result; };
    reader.readAsDataURL(blob);
  } catch (err) {
    console.error("Snapshot failed:", err);
  }
};

const retakePhoto = () => { photoData.value = null; };

// --- NAVIGATION & ACTIONS ---
const proceedToCamera = () => {
  if (!selectedResident.value) return;
  if (selectedResident.value.has_rfid) { showErrorModal.value = true; return; }
  if (selectedResident.value.has_pending) { showPendingModal.value = true; return; }
  verifyMonth.value = ""; verifyDay.value = ""; verifyYear.value = "";
  verificationError.value = "";
  showVerificationModal.value = true;
};

const handleVerification = async () => {
  if (!verifyMonth.value || !verifyDay.value || !verifyYear.value) {
    verificationError.value = "Please complete the date."; return;
  }
  const inputDate = `${verifyYear.value}-${verifyMonth.value}-${verifyDay.value}`;
  isVerifying.value = true; verificationError.value = "";
  try {
    const { data: result } = await verifyBirthdate({ resident_id: selectedResident.value.resident_id, birthdate: inputDate });
    if (result.verified) {
      showVerificationModal.value = false;
      isCheckingRequirements.value = true;
      try {
        const { data: reqResult } = await checkIDRequirements(selectedResident.value.resident_id);
        requirementsChecks.value = reqResult.checks;
        isEligible.value = reqResult.eligible;
      } catch { requirementsChecks.value = []; isEligible.value = true; }
      finally { isCheckingRequirements.value = false; }
      showRequirementsModal.value = true;
    } else {
      verificationError.value = "Birthdate does not match our records.";
    }
  } catch { verificationError.value = "Verification failed. Please try again."; }
  finally { isVerifying.value = false; }
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
    } catch { useManualEntry.value = true; }
    finally { isFetchingAutofill.value = false; }
  }
  try {
    const { data: idData } = await generateBrgyID();
    brgyIdNumber.value = idData.brgy_id_number;
  } catch { brgyIdNumber.value = ""; }
  currentPhase.value = "details";
};

const proceedToCameraFromDetails = () => {
  if (!validateDetails()) return;
  currentPhase.value = "camera";
  startCamera();
};

const goBack = () => {
  if (isCountingDown.value) return;
  if (currentPhase.value === "camera") { stopCamera(); photoData.value = null; currentPhase.value = "details"; }
  else if (currentPhase.value === "details") { currentPhase.value = "selection"; }
  else { router.push("/id-services"); }
};

const handleReset = () => {
  lastNameLetter.value = ""; firstNameLetter.value = "";
  selectedResident.value = null; residentList.value = [];
};

const submitApplication = async () => {
  if (!selectedResident.value || !photoData.value) return;
  isSubmitting.value = true; stopCamera();
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
    const msg = err?.response?.data?.detail || "Submission failed. Please try again.";
    console.error("ID application failed:", msg);
    startCamera();
  } finally { isSubmitting.value = false; }
};

const handleModalDone = () => router.push("/id-services");

onMounted(loadIDFields);
onUnmounted(() => { stopCamera(); });

const selectLastNameLetter = (letter) => { lastNameLetter.value = letter; showLastNameDropdown.value = false; selectedResident.value = null; };
const selectFirstNameLetter = (letter) => { firstNameLetter.value = letter; showFirstNameDropdown.value = false; selectedResident.value = null; };
const selectResident = (resident) => { selectedResident.value = resident; showResidentDropdown.value = false; };
const selectMonth = (m) => { verifyMonth.value = m.value; showMonthDropdown.value = false; };
const selectDay = (d) => { verifyDay.value = d; showDayDropdown.value = false; };
const selectYear = (y) => { verifyYear.value = y; showYearDropdown.value = false; };
</script>

<template>
  <div
    class="flex flex-col w-full h-full"
    :class="{ 'content-with-keyboard': showKeyboard && currentPhase === 'details' }"
  >
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack" :disabled="isCountingDown" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('applyForRFID') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('selectResidentRecord') }}</p>
      </div>
    </div>

    <!-- Main -->
    <div class="flex-1 mb-4 min-h-0">
      <div
        :class="currentPhase === 'details' ? 'h-full' : ''"
        class="w-full bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex flex-col transition-all duration-500 ease-in-out"
      >
        <!-- Resident Selection Form -->
        <div
          v-if="currentPhase === 'selection'"
          class="flex w-full h-full items-center justify-start animate-fadeIn"
        >
          <div class="w-full flex flex-col relative px-2">
            <h2 class="text-[25px] font-bold text-[#03335C] text-left">{{ t('residentSelection') }}</h2>
            <p class="text-gray-500 italic text-xs mb-6 text-left">{{ t('selectResidentToLink') }}</p>

            <div class="space-y-4 w-full">
              <div class="flex gap-10 w-full">
                <!-- Last Name Letter -->
                <div class="flex flex-1 items-center gap-3">
                  <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                    <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                    <div class="flex flex-col leading-tight">
                      <span class="text-[9px] uppercase font-bold text-gray-400">{{ t('firstLetterOf') }}</span>
                      <span class="text-[#03335C] font-black text-sm uppercase tracking-tight">{{ t('surname') }}</span>
                    </div>
                  </div>
                  <div class="flex-1 relative">
                    <button @click="toggleDropdown('lastName')" class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors">
                      {{ lastNameLetter || t('select') }}
                      <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                    </button>
                    <div v-if="showLastNameDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll">
                      <button v-for="l in alphabet" :key="l" @click="selectLastNameLetter(l)" class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]">{{ l }}</button>
                    </div>
                  </div>
                </div>

                <!-- First Name Letter -->
                <div class="flex flex-1 items-center gap-3">
                  <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                    <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
                    <div class="flex flex-col leading-tight">
                      <span class="text-[9px] uppercase font-bold text-gray-400">{{ t('firstLetterOf') }}</span>
                      <span class="text-[#03335C] font-black text-sm uppercase tracking-tight">{{ t('firstName') }}</span>
                    </div>
                  </div>
                  <div class="flex-1 relative">
                    <button @click="toggleDropdown('firstName')" class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors">
                      {{ firstNameLetter || t('select') }}
                      <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                    </button>
                    <div v-if="showFirstNameDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll">
                      <button v-for="l in alphabet" :key="l" @click="selectFirstNameLetter(l)" class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]">{{ l }}</button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Resident Name Dropdown -->
              <div class="flex items-center gap-3 w-full">
                <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
                  <UserIcon class="w-5 h-5 text-[#03335C]" />
                  <span class="text-[#03335C] font-bold text-[11px] uppercase tracking-tight">{{ t('residentName') }}</span>
                </div>
                <div class="flex-1 relative">
                  <button @click="toggleDropdown('resident')" :disabled="!lastNameLetter || !firstNameLetter || isFetching" class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors disabled:opacity-50 disabled:bg-gray-50">
                    <span v-if="isFetching" class="text-gray-400 text-sm italic">{{ t('loading') }}</span>
                    <span v-else-if="selectedResident" class="truncate text-[#03335C]">
                      {{ selectedResident.last_name }}, {{ selectedResident.first_name }}
                      <span v-if="selectedResident.middle_name">{{ selectedResident.middle_name }}</span>
                    </span>
                    <span v-else class="text-gray-400 truncate opacity-60">{{ !lastNameLetter || !firstNameLetter ? t('selectInitialsFirst') : t('selectResident') }}</span>
                    <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                  </button>
                  <div v-if="showResidentDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-[150px] overflow-y-auto custom-scroll">
                    <div v-if="residentList.length === 0" class="p-3 text-center text-gray-400 text-sm">{{ t('noRecordsFound') }}</div>
                    <button v-for="r in residentList" :key="r.resident_id" @click="selectResident(r)" class="w-full text-left py-2 px-4 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-base border-b border-gray-50 last:border-0">
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
              <DocumentTextIcon class="w-8 h-8" />{{ t('idCardDetails') }}
            </h2>
            <p class="text-gray-500 italic text-xs mb-6 text-left flex-shrink-0">{{ t('reviewIDInfo') }}</p>

            <div class="flex-1 overflow-y-auto pr-1 min-h-0 custom-scroll px-1 pt-1">
              <div v-if="isFetchingAutofill" class="flex items-center gap-3 py-6 text-[#03335C]">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#03335C]"></div>
                <span class="text-sm font-medium">{{ t('loadingResidentData') }}</span>
              </div>

              <template v-else>
                <!-- Manual override toggle (RFID users only) -->
                <div v-if="authStore.rfidUid" class="mb-5 flex items-center gap-3">
                  <input id="manualEntry" type="checkbox" v-model="useManualEntry" class="h-5 w-5 text-[#013C6D]" />
                  <label for="manualEntry" class="text-sm text-gray-700 italic cursor-pointer select-none">{{ t('enterManually') }}</label>
                </div>

                <div v-if="idFields.length === 0" class="text-sm text-gray-400 italic py-4">{{ t('noFieldsConfigured') }}</div>

                <div v-else class="grid grid-cols-2 gap-x-6 gap-y-4 pb-2">
                  <div
                    v-for="field in idFields"
                    :key="field.id || field.name"
                    :class="field.type === 'textarea' ? 'col-span-2' : 'col-span-1'"
                    class="flex flex-col"
                  >
                    <label class="block text-base font-bold text-[#003A6B] mb-2">
                      {{ field.label }}<span v-if="field.required" class="text-red-600">*</span>
                    </label>

                    <!-- Textarea -->
                    <textarea
                      v-if="field.type === 'textarea'"
                      :id="`field-${field.name}`"
                      v-model="detailsForm[field.name]"
                      :disabled="!useManualEntry && !!AUTOFILL_MAP[field.name]"
                      :placeholder="field.label"
                      @focus="focusField(field.name)"
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D] disabled:bg-gray-50 disabled:text-gray-400 resize-none"
                      rows="2"
                    ></textarea>

                    <!-- Date picker — uses its own picker, not the keyboard -->
                    <VueDatePicker
                      v-else-if="field.type === 'date'"
                      v-model="detailsForm[field.name]"
                      :enable-time-picker="false"
                      :disabled="(!useManualEntry && !!AUTOFILL_MAP[field.name]) || isSubmitting"
                      auto-apply
                      teleport-center
                      format="MM/dd/yyyy"
                      :max-date="new Date()"
                      :placeholder="field.label"
                      :ui="{ input: 'dp-match-input' }"
                    />

                    <!-- Text / number input -->
                    <input
                      v-else
                      :id="`field-${field.name}`"
                      v-model="detailsForm[field.name]"
                      :disabled="!useManualEntry && !!AUTOFILL_MAP[field.name]"
                      :type="field.type === 'number' ? 'number' : 'text'"
                      :placeholder="field.label"
                      @focus="focusField(field.name)"
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
            <div class="h-full aspect-square bg-black rounded-3xl overflow-hidden relative flex items-center justify-center">
              <img 
                v-show="!photoData"
                :src="streamSrc"
                alt="Live stream"
                class="w-full h-full object-cover transform scale-x-[-1]"
              />
              <img v-show="photoData" :src="photoData" alt="Captured ID" class="w-full h-full object-cover transform scale-x-[-1]" />
              <canvas ref="canvasRef" class="hidden"></canvas>
              <div v-if="!photoData" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <template v-if="isCountingDown">
                  <span class="text-[80px] font-black text-white drop-shadow-[0_4px_10px_rgba(0,0,0,0.8)] leading-none">{{ countdown }}</span>
                  <div class="bg-black/60 text-white px-5 py-1.5 rounded-full text-sm tracking-widest uppercase font-bold mt-3 animate-pulse backdrop-blur-sm">{{ t('lookAtCamera') }}</div>
                </template>
                <div v-else class="absolute bottom-6 bg-black/60 backdrop-blur-md text-white px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase">{{ t('alignFace') }}</div>
              </div>
            </div>
          </div>
          <div class="w-[380px] flex flex-col justify-center h-full flex-shrink-0">
            <div class="flex-1 flex flex-col justify-center">
              <h2 class="text-3xl font-bold text-[#03335C] mb-1">{{ t('captureIDPhoto') }}</h2>
              <p class="text-gray-500 italic text-sm mb-4">{{ t('takeClearPhoto') }}</p>
              <div class="bg-[#EAF6FB] rounded-2xl p-6 border border-[#BDE0EF] flex flex-col gap-3">
                <div>
                  <p class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1">{{ t('applyingFor') }}</p>
                  <p class="font-black text-[#03335C] text-xl truncate">{{ selectedResident?.first_name }} {{ selectedResident?.last_name }}</p>
                </div>
                <div class="border-t border-[#BDE0EF] pt-3">
                  <p class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1">{{ t('barangayIDNo') }}</p>
                  <p v-if="brgyIdNumber" class="font-black text-[#03335C] text-xl tracking-widest font-mono">{{ brgyIdNumber }}</p>
                  <p v-else class="text-gray-400 text-sm italic">{{ t('generating') }}</p>
                </div>
              </div>
            </div>
            <div class="flex gap-3 mt-4">
              <template v-if="!photoData">
                <Button :variant="isCountingDown ? 'disabled' : 'primary'" size="md" class="w-full justify-center text-lg py-4" :disabled="isCountingDown" @click="startCountdown">
                  <span class="flex items-center justify-center gap-2 w-full">
                    <CameraIcon v-if="!isCountingDown" class="w-6 h-6" />
                    {{ isCountingDown ? t('getReady') : t('capturePhoto') }}
                  </span>
                </Button>
              </template>
              <template v-else>
                <Button variant="outline" size="md" class="w-full justify-center text-lg py-3" @click="retakePhoto" :disabled="isSubmitting">{{ t('retake') }}</Button>
                <Button :variant="isSubmitting ? 'disabled' : 'secondary'" size="md" class="w-full justify-center text-lg py-4" :disabled="isSubmitting" @click="submitApplication">
                  {{ isSubmitting ? t('processing') : t('submit') }}
                </Button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom action buttons -->
    <div v-if="currentPhase === 'selection'" class="flex gap-6 mt-6 justify-between items-center flex-shrink-0">
      <Button variant="outline" size="md" @click="handleReset" :disabled="!lastNameLetter && !firstNameLetter && !selectedResident">{{ t('resetSelection') }}</Button>
      <Button :variant="selectedResident ? 'secondary' : 'disabled'" size="md" :disabled="!selectedResident" @click="proceedToCamera">{{ t('continueToForm') }}</Button>
    </div>

    <div v-else-if="currentPhase === 'details'" class="flex gap-6 mt-6 justify-between items-center flex-shrink-0">
      <Button variant="outline" size="md" @click="currentPhase = 'selection'">{{ t('back') }}</Button>
      <Button variant="secondary" size="md" @click="proceedToCameraFromDetails">{{ t('nextTakePhoto') }}</Button>
    </div>

    <!-- Virtual Keyboard — same pattern as FeedbackComments.vue -->
    <Transition name="slide-up">
      <VirtualKeyboard
        v-if="showKeyboard && currentPhase === 'details'"
        @key-press="handleKeyPress"
        @delete="handleDelete"
        @enter="handleEnter"
        @hide-keyboard="handleHideKeyboard"
        class="fixed bottom-0 w-full z-40"
      />
    </Transition>

    <!-- Requirements Modal -->
    <Transition name="fade-blur">
      <div v-if="showRequirementsModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
        <div class="bg-white rounded-[28px] p-10 max-w-[560px] w-full shadow-2xl relative">
          <div v-if="isCheckingRequirements" class="flex flex-col items-center py-8 gap-4">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#03335C]"></div>
            <p class="text-[#03335C] font-medium">{{ t('checkingRequirements') }}</p>
          </div>
          <template v-else>
            <h2 class="text-2xl font-bold text-[#03335C] mb-1">{{ t('applicationRequirements') }}</h2>
            <p class="text-gray-500 text-sm mb-6">{{ t('requirementsCheckedFor') }} <strong>{{ selectedResident?.first_name }} {{ selectedResident?.last_name }}</strong>.</p>
            <div v-if="requirementsChecks.length === 0" class="flex items-center gap-3 py-4 px-4 bg-blue-50 rounded-2xl mb-6">
              <InformationCircleIcon class="w-6 h-6 text-blue-500 flex-shrink-0" />
              <p class="text-sm text-blue-700">{{ t('noRequirementsConfigured') }}</p>
            </div>
            <div v-else class="flex flex-col gap-3 mb-6 max-h-64 overflow-y-auto custom-scroll pr-1">
              <div
                v-for="check in requirementsChecks" :key="check.id"
                class="flex items-start gap-3 p-4 rounded-2xl border"
                :class="{ 'bg-green-50 border-green-200': check.passed === true, 'bg-red-50 border-red-200': check.passed === false, 'bg-amber-50 border-amber-200': check.passed === null && check.type === 'system_check', 'bg-blue-50 border-blue-200': check.type === 'document' }"
              >
                <div class="flex-shrink-0 mt-0.5">
                  <CheckCircleIcon v-if="check.passed === true" class="w-5 h-5 text-green-500" />
                  <XCircleIcon v-else-if="check.passed === false" class="w-5 h-5 text-red-500" />
                  <ClockIcon v-else-if="check.passed === null && check.type === 'system_check'" class="w-5 h-5 text-amber-500" />
                  <InformationCircleIcon v-else class="w-5 h-5 text-blue-500" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-bold text-sm" :class="{ 'text-green-800': check.passed === true, 'text-red-800': check.passed === false, 'text-amber-800': check.passed === null && check.type === 'system_check', 'text-blue-800': check.type === 'document' }">{{ check.label }}</p>
                  <p class="text-xs mt-0.5" :class="{ 'text-green-600': check.passed === true, 'text-red-600': check.passed === false, 'text-amber-600': check.passed === null && check.type === 'system_check', 'text-blue-600': check.type === 'document' }">{{ check.message }}</p>
                </div>
                <span class="flex-shrink-0 text-[10px] font-bold uppercase px-2 py-1 rounded-full" :class="{ 'bg-green-100 text-green-700': check.passed === true, 'bg-red-100 text-red-700': check.passed === false, 'bg-amber-100 text-amber-700': check.passed === null && check.type === 'system_check', 'bg-blue-100 text-blue-700': check.type === 'document' }">
                  {{ check.passed === true ? t('passed') : check.passed === false ? t('failed') : check.type === 'document' ? t('bringThis') : t('pending') }}
                </span>
              </div>
            </div>
            <div v-if="!isEligible" class="flex items-start gap-3 p-4 bg-red-50 rounded-2xl border border-red-200 mb-6">
              <XCircleIcon class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p class="text-sm text-red-700 font-medium">{{ t('ineligibleWarning') }}</p>
            </div>
            <div class="flex gap-4 mt-2">
              <Button variant="outline" class="flex-1" @click="showRequirementsModal = false">{{ t('cancel') }}</Button>
              <Button v-if="isEligible" variant="secondary" class="flex-1" @click="proceedFromRequirements">{{ t('proceedToApplication') }}</Button>
              <Button v-else variant="disabled" class="flex-1" disabled>{{ t('cannotProceed') }}</Button>
            </div>
          </template>
        </div>
      </div>
    </Transition>

    <!-- Birthdate Verification Modal -->
    <Transition name="fade-blur">
      <div v-if="showVerificationModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
        <div class="bg-white rounded-[28px] p-10 max-w-[500px] w-full shadow-2xl relative">
          <h2 class="text-2xl font-bold text-[#03335C] mb-2">{{ t('verifyIdentity') }}</h2>
          <p class="text-gray-500 text-sm mb-6">{{ t('enterBirthdateFor') }} <strong>{{ selectedResident?.first_name }} {{ selectedResident?.last_name }}</strong> {{ t('toProceed') }}.</p>
          <div class="flex gap-3 mb-4">
            <div class="flex-1 relative">
              <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">{{ t('month') }}</label>
              <button @click="toggleDropdown('month')" class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]">
                {{ months.find((m) => m.value === verifyMonth)?.name || t('select') }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div v-if="showMonthDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll">
                <button v-for="m in months" :key="m.value" @click="selectMonth(m)" class="w-full text-left py-2 px-3 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm">{{ m.name }}</button>
              </div>
            </div>
            <div class="flex-1 relative">
              <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">{{ t('day') }}</label>
              <button @click="toggleDropdown('day')" class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]">
                {{ verifyDay || t('dd') }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div v-if="showDayDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll">
                <button v-for="d in days" :key="d" @click="selectDay(d)" class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm">{{ d }}</button>
              </div>
            </div>
            <div class="flex-1 relative">
              <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">{{ t('year') }}</label>
              <button @click="toggleDropdown('year')" class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]">
                {{ verifyYear || t('yyyy') }}
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div v-if="showYearDropdown" class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll">
                <button v-for="y in years" :key="y" @click="selectYear(y)" class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm">{{ y }}</button>
              </div>
            </div>
          </div>
          <p v-if="verificationError" class="text-red-500 text-xs font-bold mb-4 animate-shake">{{ verificationError }}</p>
          <div class="flex gap-4 mt-8">
            <Button variant="outline" class="flex-1" :disabled="isVerifying" @click="showVerificationModal = false">{{ t('cancel') }}</Button>
            <Button :variant="isVerifying ? 'disabled' : 'secondary'" class="flex-1" :disabled="isVerifying" @click="handleVerification">{{ isVerifying ? t('verifying') : t('verifyAndProceed') }}</Button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Success Modal -->
    <Transition name="fade-blur">
      <div v-if="showSuccessModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
        <Modal :title="t('applicationReceived')" :message="t('applicationReceivedMsg')" :reference-id="referenceId" :show-reference-id="true" :show-primary-button="true" :show-secondary-button="false" :primary-button-text="t('done')" @primary-click="handleModalDone" />
      </div>
    </Transition>

    <!-- Error Modal: Active RFID already exists -->
    <Transition name="fade-blur">
      <div v-if="showErrorModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
        <Modal :title="t('existingRFIDFound')" :message="t('existingRFIDMsg')" :show-reference-id="false" :show-primary-button="true" :show-secondary-button="false" :primary-button-text="t('close')" @primary-click="showErrorModal = false" />
      </div>
    </Transition>

    <!-- Error Modal: Pending ID application already exists -->
    <Transition name="fade-blur">
      <div v-if="showPendingModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
        <Modal :title="t('applicationAlreadyPending')" :message="t('applicationPendingMsg')" :show-reference-id="false" :show-primary-button="true" :show-secondary-button="false" :primary-button-text="t('close')" @primary-click="showPendingModal = false" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Push content up when keyboard is open — mirrors FeedbackComments.vue */
.content-with-keyboard {
  padding-bottom: 210px;
  transition: padding-bottom 0.3s ease-out;
}

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background-color: #bde0ef; border-radius: 20px; }

.modal-backdrop { backdrop-filter: blur(8px); }

.fade-blur-enter-active,
.fade-blur-leave-active { transition: opacity 0.5s ease, backdrop-filter 0.5s ease; }
.fade-blur-enter-from,
.fade-blur-leave-to { opacity: 0; backdrop-filter: blur(0px); }
.fade-blur-enter-to,
.fade-blur-leave-from { opacity: 1; backdrop-filter: blur(8px); }

/* Identical transition name and keyframes as FeedbackComments.vue */
.slide-up-enter-active,
.slide-up-leave-active { transition: transform 0.3s ease-out; }
.slide-up-enter-from,
.slide-up-leave-to { transform: translateY(100%); }

.animate-fadeIn { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

.animate-shake { animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>

<style>
.dp-match-input.dp__input {
  height: 48px !important;
  border-radius: 0.75rem !important;
  border: 1px solid #d1d5db !important;
  padding: 0.75rem 1rem 0.75rem 2.5rem !important;
  font-size: 1rem !important;
  color: #111827 !important;
  background-color: #ffffff !important;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
  line-height: normal !important;
}
.dp-match-input.dp__input:focus {
  border-color: #013C6D !important;
  box-shadow: 0 0 0 2px #013C6D !important;
}
.dp-match-input.dp__input_readonly,
.dp-match-input.dp__input:disabled {
  background-color: #f3f4f6 !important;
  color: #374151 !important;
  cursor: not-allowed !important;
}
</style>