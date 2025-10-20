<script setup>
import { ref, computed } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import PrimaryButton from '@/components/shared/PrimaryButton.vue'
import { CalendarIcon } from '@heroicons/vue/24/outline'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

// --- Props & Emits ---
const props = defineProps({
  selectedEquipment: Array,
  selectedDates: Object,
  goNext: Function,
  goBack: Function,
})
const emit = defineEmits(['update:selected-dates'])

// --- Local State ---
const borrowDate = ref(props.selectedDates?.borrow || null)
const returnDate = ref(props.selectedDates?.return || null)

// --- Computed Properties ---
const numberOfDays = computed(() => {
  if (!borrowDate.value || !returnDate.value) {
    return 1 // Default to 1 day as per the design
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

// --- Methods ---
const formatCurrency = (value) => {
  return `$${value.toLocaleString()}`
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
</script>

<template>
  <div class="pb-8">
    
    <div class="flex items-center gap-4">
      <ArrowBackButton @click="handleBack" />
      <h1 class="text-3xl font-bold text-[#013C6D]">Equipment Borrowing</h1>
    </div>

    <div class="mt-8 grid grid-cols-5 gap-8 items-stretch">
      
      <div class="col-span-2">
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-full min-h-[300px]">
          <h3 class="text-[23px] font-bold text-[#013C6D] flex items-center gap-2">
            <CalendarIcon class="w-6 h-6" />
            Select Borrowing Dates
          </h3>
          <div class="mt-8 space-y-6">
            <div>
              <label for="borrow-date" class="block text-base font-medium text-gray-700">
                Borrow Date *
              </label>
              <VueDatePicker
                id="borrow-date"
                v-model="borrowDate"
                placeholder="Borrow Date *"
                :enable-time-picker="false"
                auto-apply
                teleport-center
                format="MM/dd/yyyy"
                input-class-name="w-full pl-10 pr-3 py-3 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#013C6D] focus:border-transparent"
              >
                <template #input-icon>
                  <CalendarIcon class="w-5 h-5 text-gray-400 ml-3" />
                </template>
              </VueDatePicker>
            </div>
            <div>
              <label for="return-date" class="block text-base font-medium text-gray-700">
                Return Date *
              </label>
              <VueDatePicker
                id="return-date"
                v-model="returnDate"
                placeholder="Return Date *"
                :enable-time-picker="false"
                auto-apply
                teleport-center
                format="MM/dd/yyyy"
                :min-date="borrowDate"
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
        <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6 h-full min-h-[310px]">
          <h3 class="text-2xl font-bold text-[#013C6D]">Cost Breakdown</h3>
          <ul class="mt-6 space-y-3">
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
            <span>{{ formatCurrency(totalCost) }}</span>
          </div>
        </div>
      </div>
    </div> 
    
    <div class="mt-8 grid grid-cols-2 gap-8">
      <PrimaryButton
        @click="handleBack"
        bgColor="bg-gray-400"
        borderColor="border-gray-400"
        class="py-3 text-lg font-bold"
      >
        Back to Items
      </PrimaryButton>

      <PrimaryButton
        @click="handleNext"
        class="py-3 text-lg font-bold"
        :disabled="!borrowDate || !returnDate"
        :bgColor="(!borrowDate || !returnDate) ? 'bg-gray-400' : 'bg-[#013C6D]'"
        :borderColor="(!borrowDate || !returnDate) ? 'border-gray-400' : 'border-[#013C6D]'"
      >
        Continue to Form
      </PrimaryButton>
    </div>

  </div>
</template>

<style>
/* Global style for the date picker pop-up */
.dp__theme_light {
  --dp-font-family: 'Poppins', sans-serif;
  --dp-border-radius: 8px; /* rounded-lg */
  --dp-primary-color: #013C6D; /* Your main blue */
}
</style>