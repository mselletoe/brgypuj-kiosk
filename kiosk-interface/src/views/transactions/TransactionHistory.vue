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
    createdAt: '2024-09-09',
    status: 'completed'
  },
  {
    id: 2,
    type: 'equipment',
    reference: 'EB-1023',
    title: '2x Tents, 30x Monoblocs',
    createdAt: '2024-09-09',
    status: 'completed'
  },
  {
    id: 3,
    type: 'document',
    reference: 'DR-1291',
    title: 'Barangay Clearance',
    createdAt: '2024-09-09',
    status: 'rejected'
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
    <div
      class="flex flex-col w-full bg-white rounded-2xl shadow-lg border border-gray-200 p-4"
      style="padding: 35px; box-shadow: 0 15px 40px rgba(0,1,4,0.1);"
    >
      <div class="flex flex-col gap-6 w-full">
        <TransactionCard
          v-for="item in transactions"
          :key="item.id"
          :type="item.type"
          :reference="item.reference"
          :title="item.title"
          :createdAt="item.createdAt"
          :status="item.status"
        />
      </div>
    </div>

  </div>
</template>
