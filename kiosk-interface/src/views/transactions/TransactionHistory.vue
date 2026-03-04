<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import TransactionCard from '@/views/transactions/TransactionHistoryCard.vue'
import { useAuthStore } from '@/stores/auth'
import { getTransactionHistory } from '@/api/transactionService'

const router = useRouter()
const auth = useAuthStore()
const goBack = () => router.push('/home')

const transactions = ref([])
const isLoading = ref(false)
const error = ref(null)

/**
 * Maps the backend response shape to the props TransactionHistoryCard expects.
 *
 * Backend sends:
 * { id, transaction_type, transaction_name, transaction_no,
 * rfid_uid, status, created_at }
 *
 * Card expects:
 * { id, type, title, reference, rfidNo, createdAt, status }
 */
function mapTransaction(entry) {
  return {
    id:        entry.id,
    type:      entry.transaction_type,               // "document" | "equipment" | "rfid"
    title:     entry.transaction_name,               // "Barangay Clearance" / "2x Tent, …"
    reference: entry.transaction_no,                 // "DR-0010" / "EB-1023"
    rfidNo:    entry.rfid_uid ?? null,
    createdAt: formatDate(entry.created_at),
    status:    entry.status.toLowerCase(),           // "completed" | "rejected"
  }
}

function formatDate(isoString) {
  if (!isoString) return '—'
  return new Date(isoString).toLocaleDateString('en-PH', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

async function fetchHistory() {
  if (!auth.residentId) return

  isLoading.value = true
  error.value = null

  try {
    const data = await getTransactionHistory(auth.residentId)
    transactions.value = data.map(mapTransaction)
  } catch (err) {
    error.value = 'Failed to load transaction history. Please try again.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchHistory)
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

    <div class="flex flex-col w-full bg-white p-8 shadow-lg rounded-2xl border border-gray-200 overflow-y-auto mb-3">

      <div v-if="isLoading" class="flex flex-col justify-center items-center py-20">
        <div class="loader-dots mb-4">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <p class="text-[#03335C] text-lg font-semibold">Loading transactions...</p>
      </div>

      <div v-else-if="error" class="flex justify-center items-center py-16">
        <p class="text-red-500 text-base font-medium">{{ error }}</p>
      </div>

      <div v-else-if="transactions.length === 0" class="flex justify-center items-center py-16">
        <p class="text-gray-400 text-base font-medium">No transactions found.</p>
      </div>

      <div v-else class="flex flex-col gap-4 w-full">
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

<style scoped>
/* Loader Dots CSS */
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
  background-color: #03335C; 
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
  0%, 80%, 100% { 
    transform: scale(0); 
    opacity: 0.3; 
  }
  40% { 
    transform: scale(1); 
    opacity: 1;
  }
}
</style>