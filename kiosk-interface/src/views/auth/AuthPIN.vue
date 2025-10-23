<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/api'
import { login } from '@/stores/auth'

const router = useRouter()
const route = useRoute()

const pin = ref('')
const confirmPin = ref('')
const residentId = ref(null)
const residentName = ref('')
const hasPin = ref(false)
const isSettingPin = ref(false)
const mode = ref('user')
const ADMIN_PIN = '7890' // Changeable later if needed

onMounted(async () => {
  mode.value = route.query.mode || 'user'
  console.log('🧭 Mode:', mode.value, 'UID:', route.query.uid)

  // --- Admin PIN Mode ---
  if (mode.value === 'admin') {
    return // no need to load user data
  }

  // --- Resident PIN Mode ---
  residentId.value = route.query.resident_id
  if (!residentId.value) {
    alert('No user ID found. Please scan RFID again.')
    router.push('/login-rfid')
    return
  }

  try {
    const res = await api.get(`/users/${residentId.value}/pin`)
    hasPin.value = res.data.has_pin
    isSettingPin.value = !hasPin.value

    const userRes = await api.get(`/users/${residentId.value}`)
    residentName.value = `${userRes.data.first_name} ${userRes.data.last_name}`
  } catch (err) {
    alert('Error checking PIN. Please try again.')
  }
})

const submitPin = async () => {
  if (!pin.value) return alert('Please enter a PIN')

  // ----------------------------
  // ADMIN MODE (unlinked RFID)
  // ----------------------------
  if (mode.value === 'admin') {
    if (pin.value === ADMIN_PIN) {
      const userData = { name: 'Admin', isAdmin: true }
      login(userData)
      localStorage.setItem('auth_user', JSON.stringify({ user: userData, isGuest: false }))
      const uid = route.query.uid
      router.replace(`/register?uid=${uid}`)
    } else {
      alert('❌ Invalid Admin PIN')
    }
    return
  }

  // ----------------------------
  // USER MODE (linked RFID)
  // ----------------------------
  if (isSettingPin.value) {
    // For first-time setup
    await api.post(`/users/${residentId.value}/pin`, { pin: pin.value })
    alert('✅ PIN set successfully!')
  } else {
    // For returning users
    const res = await api.post(`/users/${residentId.value}/pin/verify`, { pin: pin.value })
    if (!res.data.valid) return alert('❌ Invalid PIN')
  }

  const userData = { id: residentId.value, name: residentName.value }
  login(userData)
  localStorage.setItem('auth_user', JSON.stringify({ user: userData, isGuest: false }))
  router.replace('/home')
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex flex-col justify-center items-center font-poppins">
    <div class="bg-white w-[500px] h-[400px] rounded-lg shadow-2xl flex flex-col justify-center items-center p-8 gap-6">
      <h2 class="text-3xl font-semibold text-gray-700">
        {{ mode === 'admin' ? 'Admin PIN' : (isSettingPin ? 'Set Your PIN' : 'Enter PIN') }}
      </h2>

      <p v-if="mode === 'admin'" class="text-gray-500 text-sm text-center">
        Enter admin PIN to proceed with registration.
      </p>

      <input 
        type="password" 
        v-model="pin" 
        class="input input-bordered w-64 text-xl text-center" 
        placeholder="PIN"
      />

      <input 
        v-if="mode === 'user' && isSettingPin" 
        type="password" 
        v-model="confirmPin" 
        class="input input-bordered w-64 text-xl text-center" 
        placeholder="Confirm PIN"
      />

      <button @click="submitPin" class="btn btn-primary w-64 h-16 text-2xl">
        Submit
      </button>
    </div>
  </div>
</template>