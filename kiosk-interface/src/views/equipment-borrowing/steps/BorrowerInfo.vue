<script setup>
import { ref, computed, nextTick, watch } from 'vue';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import Button from '@/components/shared/Button.vue';
import Modal from '@/components/shared/Modal.vue';
import Keyboard from '@/components/shared/Keyboard.vue';
import { useAuthStore } from '@/stores/auth';
import { DocumentTextIcon } from '@heroicons/vue/24/outline';
import { getAutofillData } from '@/api/equipmentService';
import { useRouter } from 'vue-router';

const useAutofill = ref(false);
const isLoadingAutofill = ref(false);
const authStore = useAuthStore();
const residentId = computed(() => authStore.residentId);
const showKeyboard = ref(false);
const activeInput = ref(null);
const showExitModal = ref(false);
const router = useRouter();

const props = defineProps({
  borrowerInfo: Object,
  goNext: Function,
  goBack: Function,
  hasStartedForm: Function,
});

const emit = defineEmits(['update:borrower-info']);

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

const localInfo = ref({
  contactPerson: props.borrowerInfo.contactPerson || '',
  contactNumber: props.borrowerInfo.contactNumber || '',
  purpose: props.borrowerInfo.purpose || null,
  notes: props.borrowerInfo.notes || ''
});

const purposeOptions = ref([
  'Barangay Event',
  'Personal Event (Birthday, Wedding, etc.)',
  'Community Meeting',
  'Emergency Use',
  'Other'
]);

const isFormValid = computed(() => {
  return localInfo.value.contactPerson &&
         localInfo.value.contactNumber &&
         localInfo.value.purpose;
});

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

const focusInput = (elementId, fieldName) => {
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
    if (['contactPerson', 'contactNumber', 'notes'].includes(activeInput.value)) {
      localInfo.value[activeInput.value] += char;
    }
  }
};

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

const inputClass = "w-full px-4 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D]";
</script>

<template>
  <div class="flex flex-col w-full h-full" :class="{ 'content-with-keyboard': showKeyboard }">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Equipment Borrowing</h1>
        <p class="text-[#03335C] -mt-2">Provide your borrowing information below.</p>
      </div>
    </div>

    <!-- Main -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <!-- Box Title -->
        <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
          <DocumentTextIcon class="w-8 h-8" />
          Borrowing Information
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
            Autofill using my saved information
          </label>
        </div>

        <!-- Form -->
        <div class="mt-4 grid grid-cols-2 gap-x-6 gap-y-4">
          <!-- Contact Person -->
          <div>
            <label for="contact-person" class="block text-base font-bold text-[#003A6B] mb-1">
              Contact Person <span class="text-red-600">*</span>
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

          <!-- Contact Number -->
          <div>
            <label for="contact-number" class="block text-base font-bold text-[#003A6B] mb-1">
              Contact Number <span class="text-red-600">*</span>
            </label>
            <input
              id="contact-number"
              v-model="localInfo.contactNumber"
              type="tel"
              placeholder="Phone Number"
              :class="inputClass"
              @focus="focusInput('contact-number', 'contactNumber')"
              :readonly="useAutofill" 
            />
          </div>

          <!-- Purpose -->
          <div>
            <label for="purpose" class="block text-base font-bold text-[#003A6B] mb-1">
              Purpose of Borrowing <span class="text-red-600">*</span>
            </label>
            <select
              id="purpose"
              v-model="localInfo.purpose"
              :class="[inputClass, { 'text-gray-500': !localInfo.purpose }]"
            >
              <option :value="null" disabled>Select</option>
              <option v-for="option in purposeOptions" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Buttons -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        @click="handleBack"
        variant="outline"
        size="md"
      >
        Back to Dates
      </Button>

      <Button
        @click="handleNext"
        :disabled="!isFormValid"
        :variant="!isFormValid ? 'disabled' : 'secondary'"
        size="md"
      >
        Review Request
      </Button>
    </div>
  </div>

  <!-- Keyboard -->
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

  <!-- Exit Confirmation Modal -->
  <div v-if="showExitModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
    <Modal
      title="Exit Equipment Request?"
      message="You have unsaved changes. Are you sure you want to exit? All your progress will be lost."
      primaryButtonText="Exit"
      secondaryButtonText="Stay"
      :showPrimaryButton="true"
      :showSecondaryButton="true"
      :showReferenceId="false"
      @primary-click="confirmExit"
      @secondary-click="cancelExit"
    />
  </div>
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
</style>