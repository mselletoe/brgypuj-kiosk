<script setup>
import { ref, computed, nextTick } from 'vue';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue';
import Button from '@/components/shared/Button.vue';
import Keyboard from '@/components/shared/Keyboard.vue';
import { DocumentTextIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  borrowerInfo: Object,
  goNext: Function,
  goBack: Function,
});
const emit = defineEmits(['update:borrower-info']);

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

const showKeyboard = ref(false);
const activeInput = ref(null);

const isFormValid = computed(() => {
  return localInfo.value.contactPerson &&
         localInfo.value.contactNumber &&
         localInfo.value.purpose;
});

const handleBack = () => {
  props.goBack('dates');
};

const handleNext = () => {
  emit('update:borrower-info', localInfo.value);
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

const inputClass = "w-full px-4 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D]";
</script>

<template>
  <div class="flex flex-col w-full h-full" :class="{ 'content-with-keyboard': showKeyboard }">
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBackToHome" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Equipment Borrowing</h1>
        <p class="text-[#03335C] -mt-2">Provide your borrowing information below.</p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h3 class="text-2xl font-bold text-[#013C6D] flex items-center gap-2">
          <DocumentTextIcon class="w-8 h-8" />
          Borrowing Information
        </h3>

        <div class="mt-6 grid grid-cols-2 gap-x-6 gap-y-4">

          <div>
            <label for="contact-person" class="block text-base font-medium text-gray-700 mb-1">
              Contact Person *
            </label>
            <input
              id="contact-person"
              v-model="localInfo.contactPerson"
              type="text"
              placeholder="Name"
              :class="inputClass"
              @focus="focusInput('contact-person', 'contactPerson')"
              :readonly="!showKeyboard" 
            />
          </div>

          <div>
            <label for="contact-number" class="block text-base font-medium text-gray-700 mb-1">
              Contact Number *
            </label>
            <input
              id="contact-number"
              v-model="localInfo.contactNumber"
              type="tel"
              placeholder="Phone Number"
              :class="inputClass"
              @focus="focusInput('contact-number', 'contactNumber')"
              :readonly="!showKeyboard" 
            />
          </div>

          <div>
            <label for="purpose" class="block text-base font-medium text-gray-700 mb-1">
              Purpose of Borrowing *
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

          <div>
            <label for="notes" class="block text-base font-medium text-gray-700 mb-1">
              Additional Notes (Optional)
            </label>
            <textarea
              id="notes"
              v-model="localInfo.notes"
              rows="3"
              placeholder="Any additional notes or special requirements"
              :class="inputClass"
              @focus="focusInput('notes', 'notes')"
              readonly
            ></textarea>
          </div>
        </div>
      </div>
    </div>


    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        @click="handleBack"
        variant="outline"
        size="lg"
      >
        Back to Dates
      </Button>

      <Button
        @click="handleNext"
        :disabled="!isFormValid"
        :variant="!isFormValid ? 'disabled' : 'secondary'"
        size="lg"
      >
        Review Request
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
</template>

<style scoped>
select:invalid,
select[value="null"] {
  color: #6b7280;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.content-with-keyboard {
  padding-bottom: 210px;
  transition: padding-bottom 0.3s ease-out;
}
</style>