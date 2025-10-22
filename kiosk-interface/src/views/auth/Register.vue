<script setup>
import { ref, watch, onMounted } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import api from '@/api/api'
import { useRoute, useRouter } from 'vue-router'

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const route = useRoute()
const router = useRouter()

// filters
const lastNameLetter = ref('A')
const firstNameLetter = ref('A')

// data and states
const residents = ref([])  
const selectedResidentId = ref('')
const residentDetails = ref({})
const registrationSummary = ref({ idNum: '', name: '' })

// the scanned UID from LoginRFID.vue
const scannedUid = ref(route.query.uid || '')


// --- Fetch filtered residents ---
const fetchResidents = async () => {
  try {
    const res = await api.get('/residents/filter', {
      params: {
        last_letter: lastNameLetter.value,
        first_letter: firstNameLetter.value,
      },
    })
    residents.value = res.data
  } catch (err) {
    console.error('❌ Failed to fetch residents:', err)
  }
}

// --- Watchers ---
watch([lastNameLetter, firstNameLetter], fetchResidents, { immediate: true })

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

// --- Register RFID ---
const handleRegister = async () => {
  console.log('🧠 handleRegister triggered') // add this
  // --- Check for required fields ---
  if (!scannedUid.value) {
    alert('⚠️ No RFID UID detected. Please scan a card first.')
    return
  }

  console.log('🔗 Attempting to link RFID:', scannedUid.value, selectedResidentId.value)

  if (!selectedResidentId.value) {
    alert('⚠️ Please select a resident first.')
    return
  }

  // --- Prevent registering someone who already has an RFID ---
  const selectedResident = residents.value.find(r => r.id === selectedResidentId.value)
  if (selectedResident?.has_rfid) {
    alert('⚠️ This resident already has a registered RFID.')
    return
  }

  try {
    // --- Send registration request ---
    const res = await api.post('/rfid/register', {
      resident_id: selectedResidentId.value,
      rfid_uid: scannedUid.value,
    })

    // --- Success feedback ---
    console.log('✅ RFID linked:', res.data)
    alert(`✅ RFID successfully linked to ${registrationSummary.value.name}!`)

    // --- Small delay for UX before redirect ---
    setTimeout(() => router.push('/rfid-success'), 500)

  } catch (err) {
    console.error('❌ Error linking RFID:', err)

    // --- Handle common backend errors gracefully ---
    const msg = err.response?.data?.detail || ''

    if (msg.includes('already registered')) {
      alert('⚠️ This RFID tag is already linked to another resident.')
    } else if (msg.includes('Resident not found')) {
      alert('⚠️ Resident not found. Please try again.')
    } else {
      alert('❌ An unexpected error occurred while linking RFID.')
    }
  }
}

// --- Reset filters and selections ---
const handleReset = () => {
  lastNameLetter.value = 'A'
  firstNameLetter.value = 'A'
  selectedResidentId.value = ''
  residents.value = []
  residentDetails.value = {}
  registrationSummary.value = { idNum: '', name: '' }
}

// --- Go back button ---
const goBackToHome = () => {
  router.push('/login')
}

// --- Mounted ---
onMounted(() => {
  if (!route.query.uid) {
    alert('⚠️ No RFID UID detected. Please scan a card first.');
    router.push('/login');
    return;
  }
  scannedUid.value = route.query.uid;
  console.log('📡 Scanned UID detected:', scannedUid.value);
});
</script>

<template>
  <div class="py-0 p-8">
    <div class="flex flex-col items-center gap-6">
      <!-- Header -->
      <div class="header flex gap-4 w-full items-center mb-4">
        <ArrowBackButton @click="goBackToHome" />
        <div class="flex justify-between w-full">
          <h1 class="text-4xl font-bold text-[#013C6D]">Link RFID to Resident</h1>
          <h1 class="text-4xl font-light text-[#013C6D]">
            {{ scannedUid || 'No UID detected' }}
          </h1>
        </div>
      </div>

      <div class="flex gap-8 w-full">
        <!-- Left Panel -->
        <div class="bg-white rounded-2xl shadow-lg p-8 flex-1 border-2 border-[#C1C1C1] text-[#003A6B]">
          <!-- Last Name Selection -->
          <div class="mb-5 flex items-center gap-4">
            <label class="flex items-center gap-2 font-medium flex-1">
              Select first letter of your <span class="font-bold">LAST NAME</span>
            </label>
            <select
              v-model="lastNameLetter"
              class="w-20 px-3 py-1 border-2 border-gray-300 rounded-lg text-center focus:outline-none focus:border-blue-500 text-gray-700"
            >
              <option v-for="letter in alphabet" :key="letter" :value="letter">{{ letter }}</option>
            </select>
          </div>

          <!-- First Name Selection -->
          <div class="mb-5 flex items-center gap-4">
            <label class="flex items-center gap-2 font-medium flex-1">
              Select first letter of your <span class="font-bold">FIRST NAME</span>
            </label>
            <select
              v-model="firstNameLetter"
              class="w-20 px-3 py-1 border-2 border-gray-300 rounded-lg text-center focus:outline-none focus:border-blue-500 text-gray-700"
            >
              <option v-for="letter in alphabet" :key="letter" :value="letter">{{ letter }}</option>
            </select>
          </div>

          <!-- Resident Selection -->
          <div class="mb-6">
            <label class="flex items-center gap-2 font-medium mb-2">Select Resident</label>
            <select
              v-model="selectedResidentId"
              class="w-full px-4 py-1 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-gray-700"
            >
              <option disabled value="">Select Resident</option>
              <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}
                {{ resident.has_rfid ? '🔒' : '🆕' }}
              </option>
            </select>
          </div>

          <!-- Resident Details -->
          <div class="bg-gray-50 rounded-lg p-3">
            <h3 class="font-bold mb-1">Resident Details</h3>
            <p class="text-sm"><span class="font-medium">Birthday:</span> {{ residentDetails.birthday || '—' }}</p>
            <p class="text-sm"><span class="font-medium">Address:</span> {{ residentDetails.address || '—' }}</p>
          </div>
        </div>

        <!-- Right Panel -->
        <div class="w-80 flex flex-col gap-4 text-[#003A6B]">
          <div class="bg-[#E4F5FC] rounded-2xl shadow-lg p-6 border-2 border-[#A3CDDE]">
            <h2 class="font-bold text-2xl text-center mb-6">Registration Summary</h2>
            <div class="space-y-3">
              <p><span class="font-bold">RFID UID:</span> {{ scannedUid }}</p>
              <p><span class="font-bold">Resident ID:</span> {{ registrationSummary.idNum }}</p>
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
            Link RFID
          </button>
        </div>
      </div>
    </div>
  </div>
</template>