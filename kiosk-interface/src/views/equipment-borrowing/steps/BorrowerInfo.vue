<script setup>
/**
 * @file views/equipment-borrowing/steps/BorrowerInfo.vue
 * @description Step 3 of the equipment borrowing wizard.
 * Collects the borrower's contact person, contact number, and purpose.
 * Supports auto-fill from the resident's profile for RFID users.
 * Uses an on-screen keyboard for touch input.
 */

import { ref, computed, nextTick, watch } from 'vue';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import Button from '@/components/shared/Button.vue';
import Modal from '@/components/shared/Modal.vue';
import Keyboard from '@/components/shared/Keyboard.vue';
import { useAuthStore } from '@/stores/auth';
import { DocumentTextIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import { getAutofillData } from '@/api/equipmentService';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  borrowerInfo: Object,
  goNext: Function,
  goBack: Function,
  hasStartedForm: Function,
});

const emit = defineEmits(['update:borrower-info']);

const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

const residentId = computed(() => authStore.residentId);

// =============================================================================
// FORM STATE
// =============================================================================
const localInfo = ref({
  contactPerson: props.borrowerInfo.contactPerson || '',
  contactNumber: props.borrowerInfo.contactNumber || '',
  purpose: props.borrowerInfo.purpose || null,
  notes: props.borrowerInfo.notes || ''
});

const isFormValid = computed(() => {
  return localInfo.value.contactPerson &&
         localInfo.value.contactNumber &&
         localInfo.value.purpose;
});

const inputClass = "w-full h-[48px] px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]";

const purposeOptions = ref([
  'Barangay Event',
  'Personal Event (Birthday, Wedding, etc.)',
  'Community Meeting',
  'Emergency Use',
  'Other'
]);

// =============================================================================
// AUTOFILL
// =============================================================================
const useAutofill = ref(false);
const isLoadingAutofill = ref(false);

const applyAutofill = async () => {
  if (!residentId.value) return;

  isLoadingAutofill.value = true;
  try {
    const data = await getAutofillData(residentId.value);
    localInfo.value.contactPerson = data.contact_person || '';
    localInfo.value.contactNumber = data.contact_number || '';
  } catch (err) {
    console.error(err);
  } finally {
    isLoadingAutofill.value = false;
  }
};

watch(useAutofill, async (enabled) => {
  if (enabled) {
    await applyAutofill();
  } else {
    localInfo.value.contactPerson = '';
    localInfo.value.contactNumber = '';
  }
});

// =============================================================================
// PURPOSE DROPDOWN
// =============================================================================
const showPurposeDropdown = ref(false);

const selectPurpose = (option) => {
  localInfo.value.purpose = option;
  showPurposeDropdown.value = false;
};

// =============================================================================
// ON-SCREEN KEYBOARD
// =============================================================================
const showKeyboard = ref(false);
const activeInput = ref(null);

const focusInput = (elementId, fieldName) => {
  showPurposeDropdown.value = false;
  activeInput.value = fieldName;
  showKeyboard.value = true;

  nextTick(() => {
    const el = document.getElementById(elementId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
};

const handleKeyboardKeyPress = (char) => {
  if (activeInput.value) {
    if (activeInput.value === 'contactNumber') {
      if (localInfo.value.contactNumber.length < 11) {
        localInfo.value.contactNumber += char
      }
    } else if (['contactPerson', 'notes'].includes(activeInput.value)) {
      localInfo.value[activeInput.value] += char
    }
  }
}

const handleKeyboardDelete = () => {
  if (activeInput.value) {
    if (['contactPerson', 'contactNumber', 'notes'].includes(activeInput.value)) {
      localInfo.value[activeInput.value] = localInfo.value[activeInput.value].slice(0, -1);
    }
  }
};

const handleKeyboardEnter = () => {
  showKeyboard.value = false;
  activeInput.value = null;
};

const handleKeyboardHide = () => {
  showKeyboard.value = false;
  activeInput.value = null;
};

// =============================================================================
// NAVIGATION
// =============================================================================
const handleBack = () => {
  props.goBack('dates');
};

const handleNext = () => {
  emit('update:borrower-info', {
    ...localInfo.value,
    use_autofill: useAutofill.value
  });
  props.goNext('review');
};

// =============================================================================
// EXIT MODAL
// =============================================================================
const showExitModal = ref(false);

const handleBackClick = () => {
  if (props.hasStartedForm && props.hasStartedForm()) {
    showExitModal.value = true;
  } else {
    router.push('/home');
  }
};

const confirmExit = () => {
  showExitModal.value = false;
  router.push('/home');
};

const cancelExit = () => {
  showExitModal.value = false;
};
</script>

<template>
  <div class="flex flex-col w-full h-full" :class="{ 'content-with-keyboard': showKeyboard }">

    <!-- HEADER -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('equipmentBorrowingTitle') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('borrowingInfo') }}</p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-5">
        <!-- Title -->
        <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
          <DocumentTextIcon class="w-8 h-8" />
          {{ t('borrowingInfoTitle') }}
        </h3>

        <!-- Checkbox -->
        <div class="mt-4 flex items-center gap-3">
          <input
            type="checkbox"
            id="use-autofill"
            v-model="useAutofill"
            class="h-5 w-5 text-[#013C6D]"
            :disabled="!residentId"
          />
          <label for="use-autofill" class="text-sm text-gray-700 italic">
            {{ t('autofillLabel') }}
          </label>
        </div>

        <!-- Form -->
        <div class="mt-4 grid grid-cols-2 gap-x-6 gap-y-4">
          <div>
            <label for="contact-person" class="block text-base font-bold text-[#003A6B] mb-2">
              {{ t('contactPerson') }} <span class="text-red-600">*</span>
            </label>
            <input
              id="contact-person"
              v-model="localInfo.contactPerson"
              type="text"
              placeholder="Name"
              :class="inputClass"
              @focus="focusInput('contact-person', 'contactPerson')"
              :readonly="useAutofill"
            />
          </div>

          <div>
            <label for="contact-number" class="block text-base font-bold text-[#003A6B] mb-2">
              {{ t('contactNumber') }} <span class="text-red-600">*</span>
            </label>
            <input
              id="contact-number"
              v-model="localInfo.contactNumber"
              type="tel"
              placeholder="Phone Number"
              :class="inputClass"
              maxlength="11"
              @focus="focusInput('contact-number', 'contactNumber')"
              :readonly="useAutofill"
            />
          </div>

          <div>
            <label class="block text-base font-bold text-[#003A6B] mb-2">
              {{ t('purposeOfBorrowing') }} <span class="text-red-600">*</span>
            </label>
            <div class="relative">
              <button
                type="button"
                @click="showPurposeDropdown = !showPurposeDropdown"
                class="w-full h-[48px] px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow flex items-center justify-between bg-white focus:outline-none focus:ring-2 focus:ring-[#013C6D]"
              >
                <span :class="localInfo.purpose ? 'text-[#03335C] font-bold text-base' : 'text-gray-400 italic text-sm'">
                  {{ localInfo.purpose || t('select') }}
                </span>
                <ChevronDownIcon class="w-5 h-5 text-[#03335C] flex-shrink-0" />
              </button>
              <div
                v-if="showPurposeDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col overflow-y-auto custom-scroll"
              >
                <button
                  v-for="option in purposeOptions"
                  :key="option"
                  type="button"
                  @click="selectPurpose(option)"
                  class="w-full text-left py-2.5 px-4 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm border-b border-gray-50 last:border-0"
                >
                  {{ option }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FOOTER: BUTTONS -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button @click="handleBack" variant="outline" size="md">
        {{ t('backToDates') }}
      </Button>
      <Button
        @click="handleNext"
        :disabled="!isFormValid"
        :variant="!isFormValid ? 'disabled' : 'secondary'"
        size="md"
      >
        {{ t('reviewRequest') }}
      </Button>
    </div>
  </div>

  <Transition name="slide-up">
    <Keyboard
      v-if="showKeyboard"
      @key-press="handleKeyboardKeyPress"
      @delete="handleKeyboardDelete"
      @enter="handleKeyboardEnter"
      @hide-keyboard="handleKeyboardHide"
      :active-input-type="activeInput === 'contactNumber' ? 'tel' : 'text'"
      class="fixed bottom-0 w-full"
    />
  </Transition>

  <Transition name="fade-blur">
    <div v-if="showExitModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop">
      <Modal
        :title="t('exitEquipmentRequest')"
        :message="t('unsavedChanges')"
        type="warning"
        :primaryButtonText="t('exit')"
        :secondaryButtonText="t('stay')"
        :showPrimaryButton="true"
        :showSecondaryButton="true"
        :showReferenceId="false"
        @primary-click="confirmExit"
        @secondary-click="cancelExit"
      />
    </div>
  </Transition>
</template>

<style scoped>
.content-with-keyboard {
  padding-bottom: 210px;
  transition: padding-bottom 0.3s ease-out;
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.modal-backdrop {
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    -webkit-backdrop-filter 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  -webkit-backdrop-filter: blur(0px);
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
</style>