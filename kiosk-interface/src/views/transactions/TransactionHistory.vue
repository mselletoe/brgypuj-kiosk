<script setup>
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import TransactionCard from '@/views/transactions/TransactionHistoryCard.vue'
import { ref } from 'vue'

const router = useRouter()
const goBack = () => router.push('/home')

const transactions = ref([
  {
    id: 1,
    type: 'document',
    reference: 'DR-0010',
    title: 'Barangay Clearance',
    rfidNo: 'A3F9-2C11-8E40',
    createdAt: '2024-09-09',
    status: 'completed'
  },
  {
    id: 2,
    type: 'equipment',
    reference: 'EB-1023',
    title: '2x Tents, 30x Monoblocs',
    rfidNo: 'B7D1-4A02-1F93',
    createdAt: '2024-09-09',
    status: 'completed'
  },
  {
    id: 3,
    type: 'document',
    reference: 'DR-1291',
    title: 'Barangay Clearance',
    rfidNo: 'C2E5-9B34-7D61',
    createdAt: '2024-09-09',
    status: 'rejected'
  },
  {
    id: 4,
    type: 'rfid',
    title: 'Gate Entry Log',
    rfidNo: 'D8F3-1C57-2A84',
    createdAt: '2024-09-10',
    status: 'completed'
  }
])
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          Transaction History
        </h1>
        <p class="text-[#03335C] -mt-2">
          See your previous transactions here.
        </p>
      </div>
    </div>

    <!-- WHITE CONTAINER -->
    <div class="flex flex-col w-full bg-white p-8 shadow-lg rounded-2xl border border-gray-200 overflow-y-auto mb-3">
      <div class="flex flex-col gap-4 w-full">
        <TransactionCard
          v-for="item in transactions"
          :key="item.id"
          :type="item.type"
          :reference="item.reference"
          :title="item.title"
          :rfidNo="item.rfidNo"
          :createdAt="item.createdAt"
          :status="item.status"
        />
      </div>
    </div>

  </div>
</template>