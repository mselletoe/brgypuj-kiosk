<script setup>
import { ref, watch, onMounted } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'
import { useRoute, useRouter } from 'vue-router'

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const route = useRoute()
const router = useRouter()

const lastNameLetter = ref('A')
const firstNameLetter = ref('A')

const residents = ref([
  { id: '1', name: 'Alice Adams', birthdate: '1990-01-01', address: '123 Main St', has_rfid: false },
  { id: '2', name: 'Bob Brown', birthdate: '1985-05-12', address: '456 Oak Ave', has_rfid: true },
  { id: '3', name: 'Charlie Clark', birthdate: '1992-07-23', address: '789 Pine Rd', has_rfid: false }
])
const filteredResidents = ref([...residents.value])
const selectedResidentId = ref('')
const residentDetails = ref({})
const registrationSummary = ref({ idNum: '', name: '' })

// Filter residents locally by first letters
const filterResidents = () => {
  filteredResidents.value = residents.value.filter(
    r => r.name.split(' ')[0].startsWith(firstNameLetter.value) &&
         r.name.split(' ')[1]?.startsWith(lastNameLetter.value)
  )
}

watch([lastNameLetter, firstNameLetter], filterResidents, { immediate: true })

watch(selectedResidentId, (id) => {
  const res = residents.value.find((r) => r.id === id)
  if (res) {
    residentDetails.value = {
      birthday: res.birthdate || '—',
      address: res.address || '—',
    }
    registrationSummary.value = {
      idNum: res.id,
      name: res.name,
    }
  } else {
    residentDetails.value = {}
    registrationSummary.value = { idNum: '', name: '' }
  }
})

// --- Register Resident ---
const handleRegister = () => {
  if (!selectedResidentId.value) {
    alert('⚠️ Please select a resident first.')
    return
  }

  const selectedResident = residents.value.find(r => r.id === selectedResidentId.value)
  if (selectedResident?.has_rfid) {
    alert('⚠️ This resident is already registered.')
    return
  }

  // Simulate registration
  selectedResident.has_rfid = true
  alert(`✅ ${registrationSummary.value.name} successfully registered!`)
}

const handleReset = () => {
  lastNameLetter.value = 'A'
  firstNameLetter.value = 'A'
  selectedResidentId.value = ''
  filteredResidents.value = [...residents.value]
  residentDetails.value = {}
  registrationSummary.value = { idNum: '', name: '' }
}

const goBackToHome = () => {
  const stored = localStorage.getItem('auth_user')
  if (stored) {
    router.replace('/home')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div class="flex justify-between items-center w-full">
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Register
          </h1>
          <p class="text-[#03335C] -mt-2">
            Register a new RFID for a resident.
          </p>
        </div>

        <h1 class="text-[#03335C] font-bold text-[45px]">0921843094</h1>
      </div>

    </div>

    <div class="flex flex-1 gap-8 w-full">
      <!-- Left Panel -->
      <div class="bg-white rounded-2xl shadow-lg p-6 flex-1 border-2 border-[#C1C1C1] text-[#003A6B]">
        <p>Select a request transaction no.</p>

        <div class="grid grid-cols-4 mt-5 gap-6">
          <div class="text-[#B1202A] bg-[#FFE6E6] rounded-xl shadow-sm px-4 py-3 border-2 border-[#FBBABA] text-center font-bold text-xl">
            <p>1232</p>
          </div>
        </div>
      </div>

      <!-- Right Panel -->
      <div class="flex flex-col text-[#003A6B] bg-[#E4F5FC] rounded-2xl shadow-lg p-6 w-[400px] border-2 border-[#A3CDDE] text-center">
        <h2 class="font-bold text-2xl text-center">Resident Details</h2>
        <p class="italic text-[9px]">Please check the residents details before proceeding.</p>
        <div class="text-start mt-3">
          <p><span class="font-bold">Name:</span> {{ registrationSummary.name }}</p>
          <p><span class="font-bold">Birthdate:</span> {{ registrationSummary.birthdate }}</p>
          <p><span class="font-bold">Address:</span> {{ registrationSummary.address }}</p>
        </div>
      </div>
    </div>

    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        variant="outline"
      >
        Cancel
      </Button>
      <Button
        :variant="secondary"
      >
        Submit
      </Button>
    </div>
  </div>
</template>
