<script setup>
/**
 * @file Overview.vue
 * @description Admin dashboard overview component. Displays high-level system statistics,
 * transaction charts, and upcoming community events.
 * Updated: Added pronounced drop shadow effects (shadow-md and shadow-lg) to all containers.
 */

import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'

// Initialize NaiveUI message provider for global notifications
const message = useMessage()

// Component state and mapped data for top statistic cards
const statCards = ref([
  {
    title: 'Pending Document Requests',
    value: '12',
    subtitle: 'xxxxxx',
    bgClass: 'bg-gradient-to-r from-[#FFFFFF] to-[#CBFCFF]',
    textColor: 'text-[#373737]'
  },
  {
    title: 'Pending Equipment Requests',
    value: '8',
    subtitle: 'xxxxx',
    bgClass: 'bg-gradient-to-r from-[#FFFFFF] to-[#FCD6FF]',
    textColor: 'text-[#373737]'
  },
  {
    title: 'Borrowed Equipments',
    value: '3',
    subtitle: '3 past due',
    bgClass: 'bg-gradient-to-r from-[#FFFFFF] to-[#FFF5D3]',
    textColor: 'text-[#373737]'
  },
  {
    title: 'Total Revenue',
    value: '58',
    subtitle: 'from',
    bgClass: 'bg-gradient-to-r from-[#FFFFFF] to-[#B6FFC2]',
    textColor: 'text-[#373737]'
  }
])

// Bottom summary statistics under the chart
const bottomStats = ref([
  { value: '1234', label: 'Document Services', color: 'bg-[#7eb6d9]' },
  { value: '1234', label: 'Equipment Borrows', color: 'bg-[#c89874]' },
  { value: '1234', label: 'RFID/Barangay ID', color: 'bg-[#76c87a]' }
])

// Mock data for upcoming events list
const upcomingEvents = ref([
  { id: 1, month: 'JULY', day: '24', dayName: 'Wednesday', title: 'Birthday ni Mayor', location: 'Location', date: 'Date', time: 'Time' },
  { id: 2, month: 'JULY', day: '24', dayName: 'Wednesday', title: 'Birthday ni Mayor', location: 'Location', date: 'Date', time: 'Time' },
  { id: 3, month: 'JULY', day: '24', dayName: 'Wednesday', title: 'Birthday ni Mayor', location: 'Location', date: 'Date', time: 'Time' }
])

// Lifecycle hooks
onMounted(() => {
  // Initialization logic, API calls would be triggered here
  message.success('Dashboard metrics loaded successfully', { duration: 3000 })
})
</script>

<template>
  <div class="flex flex-col w-full min-h-screen bg-[#EEF2F9] gap-6">

    <div class="flex w-full gap-4">
      <div
        v-for="(card, index) in statCards"
        :key="index"
        :class="['flex flex-col flex-1 p-6 rounded-xl shadow-md', card.bgClass]"
      >
        <span :class="['text-[16px] font-semibold mb-2', card.textColor]">{{ card.title }}</span>
        <span :class="['text-[40px] font-bold leading-none tracking-tight', card.textColor]">{{ card.value }}</span>
        <span :class="['text-[14px] font-medium italic mt-2', card.textColor]">{{ card.subtitle }}</span>
      </div>
    </div>

    <div class="flex w-full gap-6">

      <div class="flex flex-col flex-1 gap-4">

        <div class="flex flex-col w-full bg-white rounded-xl shadow-md p-6 h-[280px]">
          <div class="flex justify-between items-center w-full">
            <span class="text-[20px] font-semibold text-[#1F2937]">453 transactions this month</span>
            <div class="flex items-center justify-start pl-4 bg-[#ECECEC] w-[119.59px] h-[28.9px] rounded-md shadow-sm text-[16px] font-semibold text-[#1F2937] cursor-pointer">
              2026
            </div>
          </div>
          <div class="flex flex-1 items-center justify-center w-full h-full text-gray-300">
            </div>
        </div>

        <div class="flex w-full gap-3">
          <div 
            v-for="(stat, index) in bottomStats" 
            :key="index"
            class="flex flex-1 items-center gap-3 bg-white px-3 py-2 rounded-xl shadow-md"
          >
            <div :class="['w-[45px] h-[45px] rounded-lg flex-shrink-0 shadow-sm', stat.color]"></div>
            <div class="flex flex-col">
              <span class="text-[20px] font-semibold text-[#1F2937] leading-none">{{ stat.value }}</span>
              <span class="text-[14px] font-medium font-[Inter] text-[#1F2937]">{{ stat.label }}</span>
            </div>
          </div>
        </div>

      </div>

      <div class="flex flex-col w-[35%] bg-gradient-to-r from-[#0066D4] to-[#011784] rounded-xl shadow-lg p-6">
        <div class="flex justify-between items-center w-full text-white">
          <span class="text-[20px] font-bold drop-shadow-sm">Upcoming Events</span>
          <span class="text-[13px] font-semibold underline cursor-pointer hover:text-blue-200 transition-colors drop-shadow-sm">Add an event</span>
        </div>

        <div class="flex flex-col gap-3 mt-4 mb-8">
          <div 
            v-for="event in upcomingEvents" 
            :key="event.id"
            class="flex bg-white/[0.27] rounded-xl p-2 gap-4 items-center shadow-md cursor-pointer hover:bg-white/[0.35] transition-colors"
          >
            <div class="flex flex-col items-center justify-center bg-white rounded-lg w-[72px] h-[72px] flex-shrink-0 shadow-md">
              <span class="text-[10px] font-bold text-[#0F3874] uppercase tracking-wider leading-none">{{ event.month }}</span>
              <span class="text-[32px] font-extrabold text-[#0F3874] leading-none">{{ event.day }}</span>
              <span class="text-[8px] font-bold text-[#0F3874] leading-none">{{ event.dayName }}</span>
            </div>
            
            <div class="flex flex-col text-white flex-1 overflow-hidden">
              <span class="text-[20px] font-bold leading-tight truncate drop-shadow-md">{{ event.title }}</span>
              <div class="flex gap-12 mt-2 text-[13px] italic text-white/[0.85] drop-shadow-sm">
                <span>{{ event.location }}</span>
                <span>{{ event.date }}</span>
                <span>{{ event.time }}</span>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>

  </div>
</template>