<script setup>
/**
 * @file views/equipment-borrowing/steps/SelectDates.vue
 * @description Step 2 of the equipment borrowing wizard.
 * Allows the resident to select borrow and return dates.
 * Displays a live cost breakdown per item and the total rental cost
 * based on the selected borrowing period.
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'
import Modal from '@/components/shared/Modal.vue'
import { CalendarIcon } from '@heroicons/vue/24/outline'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const props = defineProps({
  selectedEquipment: Array,
  selectedDates:     Object,
  goNext:            Function,
  goBack:            Function,
  hasStartedForm:    Function,
})

const emit = defineEmits(['update:selected-dates'])

const router = useRouter()
const { t }  = useI18n()


// =============================================================================
// DATE STATE
// =============================================================================

const borrowDate = ref(props.selectedDates?.borrow || null)
const returnDate = ref(props.selectedDates?.return || null)

const minBorrowDate = computed(() => {
  const phDate = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Manila' }))
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
  if (!borrowDate.value || !returnDate.value) return 1
  const date1 = new Date(borrowDate.value)
  const date2 = new Date(returnDate.value)
  if (isNaN(date1) || isNaN(date2) || date2 < date1) return 1
  return Math.ceil(Math.abs(date2 - date1) / (1000 * 60 * 60 * 24)) + 1
})


// =============================================================================
// COST BREAKDOWN
// =============================================================================
const costBreakdown = computed(() =>
  props.selectedEquipment.map((item) => ({
    id:       item.id,
    name:     item.name,
    quantity: item.quantity,
    cost:     item.rate * item.quantity * numberOfDays.value,
  }))
)

const totalCost = computed(() =>
  costBreakdown.value.reduce((total, item) => total + item.cost, 0)
)

const formatCurrency = (value) => `₱${value.toLocaleString()}`


// =============================================================================
// NAVIGATION
// =============================================================================
const handleBack = () => props.goBack('select')

const handleNext = () => {
  emit('update:selected-dates', {
    borrow: borrowDate.value,
    return: returnDate.value,
    days:   numberOfDays.value,
  })
  props.goNext('info')
}


// =============================================================================
// EXIT MODAL
// =============================================================================

const showExitModal = ref(false)

const handleBackClick = () => {
  if (props.hasStartedForm && props.hasStartedForm()) {
    showExitModal.value = true
  } else {
    router.push('/home')
  }
}

const confirmExit = () => { showExitModal.value = false; router.push('/home') }
const cancelExit  = () => { showExitModal.value = false }
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- Header: back button and step title -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('equipmentBorrowingTitle') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('selectBorrowingDates') }}</p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div class="grid grid-cols-5 gap-8 items-stretch">

        <!-- Left panel: date pickers -->
        <div class="col-span-2">
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-full min-h-[320px]">
            <h3 class="text-[23px] font-bold text-[#013C6D] flex items-center gap-2 whitespace-nowrap">
              {{ t('selectBorrowingDatesLabel') }}
            </h3>
            <div class="mt-8 space-y-8">

              <!-- Borrow date — minimum is today in PH time -->
              <div>
                <label for="borrow-date" class="block mb-2 font-bold text-[#003A6B]">
                  {{ t('borrowDate') }} <span class="text-red-500">*</span>
                </label>
                <VueDatePicker
                  id="borrow-date"
                  v-model="borrowDate"
                  :placeholder="t('borrowDate')"
                  :enable-time-picker="false"
                  :min-date="minBorrowDate"
                  auto-apply
                  teleport-center
                  format="MM/dd/yyyy"
                  input-class-name="w-full h-[48px] pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]"
                >
                  <template #input-icon>
                    <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
                  </template>
                </VueDatePicker>
              </div>

              <!-- Return date — minimum is the selected borrow date -->
              <div>
                <label for="return-date" class="block mb-2 font-bold text-[#003A6B]">
                  {{ t('returnDate') }} <span class="text-red-500">*</span>
                </label>
                <VueDatePicker
                  id="return-date"
                  v-model="returnDate"
                  :placeholder="t('returnDate')"
                  :enable-time-picker="false"
                  :min-date="minReturnDate"
                  auto-apply
                  teleport-center
                  format="MM/dd/yyyy"
                  input-class-name="w-full h-[48px] pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D]"
                >
                  <template #input-icon>
                    <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
                  </template>
                </VueDatePicker>
              </div>

            </div>
          </div>
        </div>

        <!-- Right panel: live cost breakdown -->
        <div class="col-span-3">
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6 h-full min-h-[310px] flex flex-col">
            <h3 class="text-2xl font-bold text-[#013C6D]">{{ t('costBreakdown') }}</h3>

            <!-- Per-item cost rows -->
            <ul class="mt-6 space-y-0 flex-grow">
              <li
                v-for="item in costBreakdown"
                :key="item.id"
                class="flex justify-between text-gray-700 text-lg"
              >
                <span>
                  {{ item.name }} ({{ item.quantity }} x {{ numberOfDays }} {{ numberOfDays > 1 ? t('days') : t('day') }})
                </span>
                <span class="font-bold">{{ formatCurrency(item.cost) }}</span>
              </li>
            </ul>

            <div class="border-t border-gray-300 my-6"></div>

            <!-- Total cost -->
            <div class="flex justify-between text-3xl font-bold text-[#013C6D]">
              <span>{{ t('totalCost') }}</span>
              <span class="text-[#09AA44]">{{ formatCurrency(totalCost) }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer: back to equipment selection and proceed to borrower info -->
    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button @click="handleBack" variant="outline" size="md">
        {{ t('backToItems') }}
      </Button>
      <Button
        @click="handleNext"
        :disabled="!borrowDate || !returnDate"
        :variant="(!borrowDate || !returnDate) ? 'disabled' : 'secondary'"
        size="md"
      >
        {{ t('continue') }}
      </Button>
    </div>

  </div>

  <!-- Exit confirmation modal -->
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
.modal-backdrop {
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}

.fade-blur-enter-active,
.fade-blur-leave-active {
  transition: opacity 0.5s ease, -webkit-backdrop-filter 0.5s ease, backdrop-filter 0.5s ease;
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