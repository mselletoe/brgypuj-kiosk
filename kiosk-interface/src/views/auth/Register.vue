<script setup>
import { ref, watch } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import api from '@/api/api'

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const lastNameLetter = ref('A')
const firstNameLetter = ref('A')
const residents = ref([])  // list of fetched residents
const selectedResidentId = ref(null)
const residentDetails = ref({})
const registrationSummary = ref({ idNum: '', name: '' })

// Fetch filtered residents
const fetchResidents = async () => {
  try {
    const res = await api.get('/residents/filter', {
      params: {
        last_letter: lastNameLetter.value,
        first_letter: firstNameLetter.value
      }
    })
    residents.value = res.data
  } catch (err) {
    console.error('Failed to fetch residents:', err)
  }
}

// Watch for filter changes
watch([lastNameLetter, firstNameLetter], fetchResidents, { immediate: true })

// When a resident is selected
watch(selectedResidentId, (id) => {
  const res = residents.value.find(r => r.id === id)
  if (res) {
    residentDetails.value = {
      birthday: res.birthdate,
      address: res.address
    }
    registrationSummary.value = {
      idNum: res.id,
      name: res.name
    }
  }
})

const scannedUid = ref('0054973429') // temporary — replace with actual UID from scanner

const handleRegister = async () => {
  if (!selectedResidentId.value) {
    alert('Please select a resident.')
    return
  }

  try {
    const res = await api.post('/rfid/register', {
      resident_id: selectedResidentId.value,
      rfid_uid: scannedUid.value
    })
    alert(res.data.message)
    console.log('RFID linked:', res.data)
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || 'Error linking RFID')
  }
}

const handleReset = () => {
  lastNameLetter.value = 'D'
  firstNameLetter.value = 'A'
  selectedResidentId.value = null
  residents.value = []
  residentDetails.value = {}
  registrationSummary.value = { idNum: '', name: '' }
}

const goBackToHome = () => {
  console.log('Going back to home')
}
</script>


<template>
  <div class="py-0 pb-8">
    <div class="flex flex-col items-center gap-4 between">
      <div class="header flex gap-4 w-full items-center mb-4">
        <ArrowBackButton @click="goBackToHome" />
        <div class="flex justify-between w-full">
          <h1 class="text-4xl font-bold text-[#013C6D]">Register your RFID</h1>
          <h1 class="text-4xl font-light text-[#013C6D]">{{ registrationSummary.idNum }}</h1>
        </div>
      </div>

      <div class="flex gap-6 max-w-6xl w-full">
        <!-- Left Panel -->
        <div class="bg-white rounded-2xl shadow-lg p-8 flex-1 border-2 border-[#C1C1C1] text-[#003A6B]">
          <!-- Last Name Selection -->
          <div class="mb-5 flex items-center gap-4">
            <label class="flex items-center gap-2 font-medium flex-1">
              Select the first letter of your <span class="font-bold">LAST NAME</span>
            </label>
            <select
              v-model="lastNameLetter"
              class="w-20 px-3 py-1 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-gray-700 text-center"
            >
              <option v-for="letter in alphabet" :key="letter" :value="letter">{{ letter }}</option>
            </select>
          </div>

          <!-- First Name Selection -->
          <div class="mb-5 flex items-center gap-4">
            <label class="flex items-center gap-2 font-medium flex-1">
              Select the first letter of your <span class="font-bold">FIRST NAME</span>
            </label>
            <select
              v-model="firstNameLetter"
              class="w-20 px-3 py-1 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-gray-700 text-center"
            >
              <option v-for="letter in alphabet" :key="letter" :value="letter">{{ letter }}</option>
            </select>
          </div>

          <!-- Resident Selection -->
          <div class="mb-6">
            <label class="flex items-center gap-2 font-medium mb-2">
              Select Resident
            </label>
            <select v-model="selectedResidentId"
                    class="w-full px-4 py-1 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-gray-700">
            <option disabled value="">Select Resident</option>
            <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}
            </option>
            </select>
          </div>

          <!-- Resident Details -->
          <div class="bg-gray-50 rounded-lg">
            <h3 class="font-bold mb-1">Resident Details</h3>
            <p class="text-sm">
              <span class="font-medium">Birthday:</span> {{ residentDetails.birthday || '—' }}
            </p>
            <p class="text-sm">
              <span class="font-medium">Address:</span> {{ residentDetails.address || '—' }}
            </p>
          </div>
        </div>

        <!-- Right Panel -->
        <div class="w-80 flex flex-col gap-4 text-[#003A6B]">
          <div class="bg-[#E4F5FC] rounded-2xl shadow-lg p-6 border-2 border-[#A3CDDE]">
            <h2 class="font-bold text-2xl text-center mb-6">
              Registration<br />Summary
            </h2>
            <div class="space-y-3">
              <p><span class="font-bold">ID Num:</span> {{ registrationSummary.idNum }}</p>
              <p><span class="font-bold">Name:</span> {{ registrationSummary.name }}</p>
            </div>
          </div>

          <!-- Buttons -->
          <button
            @click="handleReset"
            class="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-xl shadow-lg transition-colors"
          >
            Reset
          </button>
          <button
            @click="handleRegister"
            class="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-4 rounded-xl shadow-lg transition-colors"
          >
            Register User
          </button>
        </div>
      </div>
    </div>
  </div>
</template>