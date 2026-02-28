<script setup>
import { ref, computed } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue';
import Modal from '@/components/shared/Modal.vue';
import { CalendarIcon } from '@heroicons/vue/24/outline'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useRouter } from 'vue-router';

const props = defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  goNext: Function,
  goBack: Function,
  hasStartedForm: Function,
})
const emit = defineEmits(['update:selected-dates'])
const router = useRouter();

const borrowDate = ref(props.selectedDates?.borrow || null)
const returnDate = ref(props.selectedDates?.return || null)
const showExitModal = ref(false);

const minBorrowDate = computed(() => {
  const now = new Date()
  const phTimeStr = now.toLocaleString("en-US", { timeZone: "Asia/Manila" })
  const phDate = new Date(phTimeStr)
  phDate.setHours(0, 0, 0, 0)
  return phDate
})

const minReturnDate = computed(() => {
  if (!borrowDate.value) return minBorrowDate.value
  const d = new Date(borrowDate.value)
  d.setHours(0, 0, 0, 0)
  return d
})

const numberOfDays = computed(() => {
  if (!borrowDate.value || !returnDate.value) {
    return 1
  }
  const date1 = new Date(borrowDate.value)
  const date2 = new Date(returnDate.value)
  if (isNaN(date1) || isNaN(date2)) return 1
  if (date2 < date1) return 1
  const diffTime = Math.abs(date2.getTime() - date1.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays + 1
})

const costBreakdown = computed(() => {
  return props.selectedEquipment.map(item => {
    const cost = item.rate * item.quantity * numberOfDays.value
    return {
      id: item.id,
      name: item.name,
      quantity: item.quantity,
      cost: cost,
    }
  })
})

const totalCost = computed(() => {
  return costBreakdown.value.reduce((total, item) => total + item.cost, 0)
})

const formatCurrency = (value) => {
  return `₱${value.toLocaleString()}`
}

const handleBack = () => {
  props.goBack('select')
}

const handleNext = () => {
  const datesToSubmit = {
    borrow: borrowDate.value,
    return: returnDate.value,
    days: numberOfDays.value,
  }
  emit('update:selected-dates', datesToSubmit)
  props.goNext('info')
}

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
  <div class="flex flex-col w-full h-full">
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Equipment Borrowing</h1>
        <p class="text-[#03335C] -mt-2">Select your borrowing dates below.</p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="grid grid-cols-5 gap-8 items-stretch">
        <div class="col-span-2">
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-full min-h-[320px]">
            <h3 class="text-[23px] font-bold text-[#013C6D] flex items-center gap-2 whitespace-nowrap">
              Select Borrowing Dates
            </h3>
            <div class="mt-8 space-y-8">
              <div>
                <label for="borrow-date" class="block mb-2 font-bold text-[#003A6B]">
                  Borrow Date <span class="text-red-500">*</span>
                </label>
                <VueDatePicker
                  id="borrow-date"
                  v-model="borrowDate"
                  placeholder="Borrow Date"
                  :enable-time-picker="false"
                  auto-apply
                  teleport-center
                  format="MM/dd/yyyy"
                  :min-date="minBorrowDate"
                  input-class-name="w-full pl-10 pr-3 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D] focus:border-transparent"
                >
                  <template #input-icon>
                    <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
                  </template>
                </VueDatePicker>
              </div>
              <div>
                <label for="return-date" class="block mb-2 font-bold text-[#003A6B]">
                  Return Date <span class="text-red-500">*</span>
                </label>
                <VueDatePicker
                  id="return-date"
                  v-model="returnDate"
                  placeholder="Return Date"
                  :enable-time-picker="false"
                  auto-apply
                  teleport-center
                  format="MM/dd/yyyy"
                  :min-date="minReturnDate"
                  input-class-name="w-full pl-10 pr-3 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D] focus:border-transparent"
                >
                  <template #input-icon>
                    <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
                  </template>
                </VueDatePicker>
              </div>
            </div>
          </div>
        </div>

        <div class="col-span-3">
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6 h-full min-h-[310px] flex flex-col">
            <h3 class="text-2xl font-bold text-[#013C6D]">Cost Breakdown</h3>
            <ul class="mt-6 space-y-0 flex-grow">
              <li 
                v-for="item in costBreakdown"
                :key="item.id"
                class="flex justify-between text-gray-700 text-lg"
              >
                <span>
                  {{ item.name }} ({{ item.quantity }} x {{ numberOfDays }} day{{ numberOfDays > 1 ? 's' : '' }})
                </span>
                <span class="font-bold">{{ formatCurrency(item.cost) }}</span>
              </li>
            </ul>
            <div class="border-t border-gray-300 my-6"></div>
            <div class="flex justify-between text-3xl font-bold text-[#013C6D]">
              <span>Total Cost:</span>
              <span class="text-[#09AA44]">{{ formatCurrency(totalCost) }}</span>
            </div>
          </div>
        </div>
      </div>       
    </div>
    
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
          @click="handleBack"
          variant="outline"
          size="md"
        >
          Back to Items
        </Button>

        <Button
          @click="handleNext"
          :disabled="!borrowDate || !returnDate"
          :variant="(!borrowDate || !returnDate) ? 'disabled' : 'secondary'"
          size="md"
        >
          Continue
        </Button>
    </div>

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
  </div>
</template>