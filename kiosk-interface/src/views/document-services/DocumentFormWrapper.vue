<script setup>
/**
 * @file views/document-services/DocumentFormWrapper.vue
 * @description Kiosk view for filling out and submitting a document request.
 * Resolves the document type from the route slug, fetches the field config,
 * auto-fills known fields for RFID users, and evaluates eligibility requirements
 * before allowing submission. Displays requirements with live pass/fail status
 * in a side panel.
 */

import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import DocumentForm from "./DocumentForm.vue";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Modal from "@/components/shared/Modal.vue";
import Button from "@/components/shared/Button.vue";
import { useAuthStore } from "@/stores/auth";
import {
  getDocumentTypes,
  createDocumentRequest,
  checkEligibility,
} from "@/api/documentService";
import { getResidentAutofillData } from "@/api/residentService";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const { t } = useI18n();

// =============================================================================
// DOCUMENT TYPE STATE
// =============================================================================
const documents = ref({});
const loadingDocuments = ref(true);
const errorDocuments = ref(null);

const docTypeSlug = computed(() =>
  route.params.docType?.toLowerCase().replace(/\s+/g, "-"),
);

const config = computed(() => documents.value[docTypeSlug.value]);

const displayTitle = computed(() => {
  if (config.value?.title) return config.value.title;
  if (!docTypeSlug.value) return "";
  return docTypeSlug.value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
});

// =============================================================================
// RESIDENT / RFID STATE
// =============================================================================
const residentData = ref(null);
const isLoadingResidentData = ref(false);

const isRfidUser = computed(() => {
  return auth.isAuthenticated && auth.residentId !== null;
});

// =============================================================================
// ELIGIBILITY STATE
// =============================================================================
const eligibilityResult = ref(null);

function formatResidencyLabel(params) {
  const raw = params?.years ?? 0;
  const totalMonths = Number.isInteger(raw)
    ? raw * 12 + (params?.months ?? 0)
    : Math.round(raw * 12);
  const years = Math.floor(totalMonths / 12);
  const months = totalMonths % 12;
  const parts = [];
  if (years > 0) parts.push(`${years} year${years !== 1 ? "s" : ""}`);
  if (months > 0) parts.push(`${months} month${months !== 1 ? "s" : ""}`);
  return `Minimum ${parts.join(" and ") || "0 months"} of residency`;
}

const mergedRequirements = computed(() => {
  const reqs = config.value?.requirements || [];

  if (!eligibilityResult.value) {
    return reqs.map((r) => ({
      ...r,
      label: r.id === "min_residency" ? formatResidencyLabel(r.params) : r.label,
      passed: null,
      message: null,
    }));
  }

  const checksMap = {};
  for (const check of eligibilityResult.value.checks) {
    checksMap[check.id] = check;
  }

  return reqs.map((r) => {
    const live = checksMap[r.id];
    const fixedLabel =
      r.id === "min_residency" ? formatResidencyLabel(r.params) : r.label;

    const fixedMessage =
      r.id === "min_residency" && live?.message
        ? `${fixedLabel} required. ${live.passed ? "Passed." : "Requirement not met."}`
        : (live?.message ?? null);

    return {
      ...r,
      label: fixedLabel,
      passed: live?.passed ?? null,
      message: fixedMessage,
    };
  });
});

const hasBlockingFailure = computed(() => {
  return mergedRequirements.value.some(
    (r) => r.type === "system_check" && r.passed === false,
  );
});

// =============================================================================
// FORM STATE
// =============================================================================
const currentStep = ref("form");
const formData = ref({});
const isSubmitting = ref(false);
const documentFormRef = ref(null);

const submitFromWrapper = () => {
  if (documentFormRef.value) {
    documentFormRef.value.handleContinue();
  }
};

// =============================================================================
// MODAL STATE
// =============================================================================
const showSuccessModal = ref(false);
const showErrorModal = ref(false);
const errorMessage = ref("");
const transactionNo = ref("");

// =============================================================================
// DATA FETCHING
// =============================================================================
const fetchDocuments = async () => {
  loadingDocuments.value = true;
  errorDocuments.value = null;
  try {
    const data = await getDocumentTypes();
    const mapping = {};
    data.forEach((doc) => {
      const slug = doc.doctype_name.toLowerCase().replace(/\s+/g, "-");
      mapping[slug] = {
        id: doc.id,
        title: doc.doctype_name,
        fields: doc.fields || [],
        requirements: doc.requirements || [],
        available: true,
      };
    });
    documents.value = mapping;
  } catch (err) {
    console.error(err);
    errorDocuments.value = "Failed to load document fields";
  } finally {
    loadingDocuments.value = false;
  }
};

const fetchResidentData = async () => {
  if (!isRfidUser.value) {
    residentData.value = null;
    return;
  }

  isLoadingResidentData.value = true;
  try {
    const data = await getResidentAutofillData(auth.residentId);
    residentData.value = data.data;
  } catch (err) {
    console.error("Failed to fetch resident data for autofill:", err);
    residentData.value = null;
  } finally {
    isLoadingResidentData.value = false;
  }
};

const fetchEligibility = async () => {
  if (!isRfidUser.value || !config.value?.id) return;

  const hasSystemChecks = config.value.requirements?.some(
    (r) => r.type === "system_check",
  );
  if (!hasSystemChecks) return;

  try {
    eligibilityResult.value = await checkEligibility(
      config.value.id,
      auth.residentId,
    );
  } catch (err) {
    console.error("Failed to fetch eligibility:", err);
    eligibilityResult.value = null;
  }
};

// =============================================================================
// ACTIONS
// =============================================================================
const goBack = () => {
  if (currentStep.value === "preview") {
    currentStep.value = "form";
  } else {
    router.push("/document-services");
  }
};

const handleDone = () => {
  router.push("/home");
};

const handleErrorDismiss = () => {
  showErrorModal.value = false;
};

const handleSubmit = async (data) => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  if (!config.value?.id) {
    alert("Invalid document type.");
    isSubmitting.value = false;
    return;
  }

  const residentId = auth.residentId || null;

  try {
    const payload = {
      doctype_id: config.value.id,
      form_data: data,
      resident_id: residentId,
    };

    const response = await createDocumentRequest(payload);

    formData.value = data;
    transactionNo.value = response.transaction_no;
    isSubmitting.value = false;

    await new Promise((resolve) => setTimeout(resolve, 100));

    showSuccessModal.value = true;
  } catch (err) {
    console.error("Document submission error:", err);

    isSubmitting.value = false;

    errorMessage.value =
      err?.response?.data?.detail ||
      "Failed to submit document request. Please try again.";

    showErrorModal.value = true;
  }
};

const handleNewRequest = () => {
  showSuccessModal.value = false;
  formData.value = {};
  router.push("/document-services");
};

// =============================================================================
// LIFECYCLE
// =============================================================================
onMounted(async () => {
  await fetchDocuments();
  await fetchResidentData();
  await fetchEligibility();
});
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- ─ HEADER ─────────────────────────────────────────────── -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ displayTitle }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          {{ t('kindlyFillUp') }}
        </p>
      </div>
    </div>

    <!-- ─ MAIN CONTENT ───────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto">
      <div class="grid grid-cols-5 gap-8 items-stretch mb-4">

        <!-- ─ LEFT PANEL ─────────────────────────────────────────────── -->
        <div class="col-span-3">
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px]">
            <div
              v-if="loadingDocuments || isLoadingResidentData"
              class="flex flex-col justify-center items-center py-8"
            >
              <div class="loader-dots mb-4">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
              <p class="text-gray-600 font-semibold">{{ t('loadingDetails') }}</p>
            </div>

            <DocumentForm
              ref="documentFormRef"
              v-else-if="config"
              :config="config"
              :initial-data="formData"
              :resident-data="residentData"
              :is-rfid-user="isRfidUser"
              :is-submitting="isSubmitting"
              @continue="handleSubmit"
            />

            <div v-else class="text-center py-12">
              <p class="text-[#003A6B] text-lg">
                {{ t('documentUnavailable') }}
              </p>
            </div>
          </div>
        </div>

        <!-- ─ RIGHT PANEL ────────────────────────────────────────────── -->
        <div class="col-span-2">
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6 min-h-[280px]">
            <h2 class="text-lg font-bold text-[#03335C] mb-2 tracking-tight">{{ t('requirements') }}</h2>
            <p class="text-sm italic text-[#03335C] mb-4 tracking-tight">
              {{ t('reviewRequirements') }}
            </p>

            <div v-if="loadingDocuments" class="flex justify-center py-10">
              <div class="loader-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>

            <div
              v-else-if="!config?.requirements?.length"
              class="flex flex-col items-center justify-center py-10 text-center"
            >
              <p class="text-sm text-[#5A8DB8]">{{ t('noRequirements') }}</p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-if="hasBlockingFailure"
                class="bg-red-50 border border-red-200 rounded-xl p-3 flex items-start gap-2"
              >
                <svg
                  class="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clip-rule="evenodd"
                  />
                </svg>
                <p class="text-xs text-red-700 font-medium">
                  {{ t('youMayNotBeEligible') }}
                </p>
              </div>

              <div
                v-for="(req, index) in mergedRequirements"
                :key="index"
                class="flex items-start gap-3 bg-white rounded-xl p-3 border"
                :class="{
                  'border-red-300 bg-red-50': req.passed === false,
                  'border-green-300 bg-green-50': req.passed === true,
                  'border-[#B0D7F8]': req.passed === null,
                }"
              >
                <div class="flex-shrink-0 mt-0.5">
                  <svg
                    v-if="req.passed === false"
                    class="w-5 h-5 text-red-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  <svg
                    v-else-if="req.passed === true"
                    class="w-5 h-5 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  <svg
                    v-else
                    class="w-5 h-5 text-[#5A8DB8]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>

                <div class="flex-1 min-w-0">
                  <p
                    class="text-sm font-semibold leading-tight"
                    :class="{
                      'text-red-700': req.passed === false,
                      'text-green-700': req.passed === true,
                      'text-[#03335C]': req.passed === null,
                    }"
                  >
                    {{ req.label }}
                  </p>

                  <span
                    class="inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full mt-1"
                    :class="
                      req.type === 'system_check'
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-amber-100 text-amber-600'
                    "
                  >
                    {{
                      req.type === "system_check" ? t('systemCheck') : t('document')
                    }}
                  </span>

                  <p
                    v-if="req.message"
                    class="text-xs mt-1"
                    :class="{
                      'text-red-600': req.passed === false,
                      'text-green-600': req.passed === true,
                      'text-[#5A8DB8]': req.passed === null,
                    }"
                  >
                    {{ req.message }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─ FOOTER ─────────────────────────────────────────────── -->
    <div class="flex gap-6 mt-6 justify-between items-center flex-shrink-0">
      <Button
        @click="goBack"
        variant="outline"
        size="md"
        :disabled="loadingDocuments || isLoadingResidentData || isSubmitting"
      >
        {{ t('cancel') }}
      </Button>

      <Button
        @click="submitFromWrapper"
        :disabled="
          loadingDocuments || isLoadingResidentData || isSubmitting || !config
        "
        :variant="
          loadingDocuments || isLoadingResidentData || isSubmitting || !config
            ? 'disabled'
            : 'secondary'
        "
        size="md"
      >
        {{ isSubmitting ? t('submittingRequest') : t('submitRequest') }}
      </Button>
    </div>

    <!-- ─ SUBMISSION LOADING ─────────────────────────────────────────────── -->
    <transition name="fade-blur">
      <div
        v-if="isSubmitting"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-2xl p-10 shadow-2xl flex flex-col items-center gap-2 min-w-[400px]"
        >
          <div class="loader-dots mb-4">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
          <p class="text-[#03335C] text-lg font-semibold mt-2">{{ t('submittingRequest') }}</p>
          <p class="text-gray-500 text-sm">
            {{ t('pleaseWaitDoc') }}
          </p>
        </div>
      </div>
    </transition>

    <!-- ─ SUCCESS MODAL ─────────────────────────────────────────────── -->
    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <Modal
          :title="t('applicationSubmitted')"
          :message="t('applicationSubmittedMsg')"
          type="success"
          :referenceId="transactionNo"
          :showReferenceId="true"
          :primaryButtonText="t('done')"
          :showPrimaryButton="true"
          :showSecondaryButton="false"
          :showNewRequest="true"
          @primary-click="handleDone"
          @new-request="handleNewRequest"
        />
      </div>
    </transition>

    <!-- ─ ERROR MODAL ─────────────────────────────────────────────── -->
    <transition name="fade-blur">
      <div
        v-if="showErrorModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <Modal
          :title="t('requestCannotBeProcessed')"
          :message="errorMessage"
          type="error"
          :primaryButtonText="t('confirm')"
          :showPrimaryButton="true"
          :showSecondaryButton="false"
          :showNewRequest="false"
          @primary-click="handleErrorDismiss"
        />
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition: opacity 0.5s ease-in-out;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
}

.loader-dots {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 60px;
  height: 15px;
}

.dot {
  width: 12px;
  height: 12px;
  background-color: #03335c;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>