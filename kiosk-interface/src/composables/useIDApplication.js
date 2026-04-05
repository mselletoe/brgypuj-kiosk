import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import {
  searchResidents,
  verifyBirthdate,
  applyForID,
  getIDApplicationFields,
  generateBrgyID,
  checkIDRequirements,
} from "@/api/idService";
import { getResidentAutofillData } from "@/api/residentService";

const AUTOFILL_MAP = {
  last_name: "last_name",
  first_name: "first_name",
  middle_name: "middle_name",
  birthdate: "birthdate",
  address: "full_address",
  phone_number: "phone_number",
};

export function useIDApplication() {
  const router = useRouter();
  const authStore = useAuthStore();
  const currentPhase = ref("selection"); // 'selection' | 'details' | 'camera'
  const lastNameLetter = ref("");
  const firstNameLetter = ref("");
  const selectedResident = ref(null);
  const residentList = ref([]);
  const isFetching = ref(false);

  async function fetchResidents(last, first) {
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
  }

  function resetSelection() {
    lastNameLetter.value = "";
    firstNameLetter.value = "";
    selectedResident.value = null;
    residentList.value = [];
  }

  const showVerificationModal = ref(false);
  const verifyMonth = ref("");
  const verifyDay = ref("");
  const verifyYear = ref("");
  const verificationError = ref("");
  const isVerifying = ref(false);

  function openVerificationModal() {
    verifyMonth.value = "";
    verifyDay.value = "";
    verifyYear.value = "";
    verificationError.value = "";
    showVerificationModal.value = true;
  }

  async function handleVerification() {
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
        await openRequirementsModal();
      } else {
        verificationError.value = "Birthdate does not match our records.";
      }
    } catch {
      verificationError.value = "Verification failed. Please try again.";
    } finally {
      isVerifying.value = false;
    }
  }

  const showRequirementsModal = ref(false);
  const requirementsChecks = ref([]);
  const isEligible = ref(true);
  const isCheckingRequirements = ref(false);

  async function openRequirementsModal() {
    isCheckingRequirements.value = true;
    showRequirementsModal.value = true;
    try {
      const { data: reqResult } = await checkIDRequirements(
        selectedResident.value.resident_id,
      );
      requirementsChecks.value = reqResult.checks;
      isEligible.value = reqResult.eligible;
    } catch {
      requirementsChecks.value = [];
      isEligible.value = true;
    } finally {
      isCheckingRequirements.value = false;
    }
  }

  const idFields = ref([]);
  const detailsForm = ref({});
  const detailsErrors = ref({});
  const useManualEntry = ref(false);
  const isFetchingAutofill = ref(false);
  const brgyIdNumber = ref("");

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
          if (parts.length === 3) {
            val = `${parts[2]}-${parts[0]}-${parts[1]}`;
          } else {
            val = String(val).slice(0, 10);
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

  async function proceedFromRequirements() {
    showRequirementsModal.value = false;
    useManualEntry.value = !authStore.rfidUid;
    buildEmptyForm();
    if (authStore.rfidUid && selectedResident.value?.resident_id) {
      isFetchingAutofill.value = true;
      try {
        const { data: autofill } = await getResidentAutofillData(
          selectedResident.value.resident_id,
        );
        applyAutofill(autofill);
      } catch {
        useManualEntry.value = true;
      } finally {
        isFetchingAutofill.value = false;
      }
    }
    try {
      const { data: idData } = await generateBrgyID();
      brgyIdNumber.value = idData.brgy_id_number;
    } catch {
      brgyIdNumber.value = "";
    }
    currentPhase.value = "details";
  }

  function proceedToCameraFromDetails() {
    if (!validateDetails()) return;
    currentPhase.value = "camera";
  }

  const photoData = ref(null);
  const isSubmitting = ref(false);
  const showSuccessModal = ref(false);
  const showErrorModal = ref(false);
  const showPendingModal = ref(false);
  const referenceId = ref("");

  async function submitApplication(photo) {
    if (!selectedResident.value || !photo) return;
    isSubmitting.value = true;
    photoData.value = photo;
    try {
      const { data: result } = await applyForID({
        resident_id: authStore.residentId || null,
        applicant_resident_id: selectedResident.value.resident_id,
        rfid_uid: authStore.rfidUid || null,
        photo,
        use_manual_data: useManualEntry.value,
        field_values: {
          brgy_id_number: brgyIdNumber.value,
          ...detailsForm.value,
        },
      });
      referenceId.value = result.transaction_no;
      showSuccessModal.value = true;
    } catch (err) {
      const msg =
        err?.response?.data?.detail || "Submission failed. Please try again.";
      console.error("ID application failed:", msg);
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  }

  function proceedToVerification() {
    if (!selectedResident.value) return;
    if (selectedResident.value.has_rfid) {
      showErrorModal.value = true;
      return;
    }
    if (selectedResident.value.has_pending) {
      showPendingModal.value = true;
      return;
    }
    openVerificationModal();
  }

  function goBack(isCountingDown = false) {
    if (isCountingDown) return;
    if (currentPhase.value === "camera") {
      photoData.value = null;
      currentPhase.value = "details";
    } else if (currentPhase.value === "details") {
      currentPhase.value = "selection";
    } else {
      router.push("/id-services");
    }
  }

  function handleModalDone() {
    router.push("/id-services");
  }

  return {
    currentPhase,
    lastNameLetter,
    firstNameLetter,
    selectedResident,
    residentList,
    isFetching,
    fetchResidents,
    resetSelection,
    proceedToVerification,

    showVerificationModal,
    verifyMonth,
    verifyDay,
    verifyYear,
    verificationError,
    isVerifying,
    handleVerification,

    showRequirementsModal,
    requirementsChecks,
    isEligible,
    isCheckingRequirements,
    proceedFromRequirements,

    idFields,
    detailsForm,
    detailsErrors,
    useManualEntry,
    isFetchingAutofill,
    brgyIdNumber,
    loadIDFields,
    proceedToCameraFromDetails,
    AUTOFILL_MAP,

    photoData,
    isSubmitting,
    submitApplication,

    showSuccessModal,
    showErrorModal,
    showPendingModal,
    referenceId,

    goBack,
    handleModalDone,
  };
}
