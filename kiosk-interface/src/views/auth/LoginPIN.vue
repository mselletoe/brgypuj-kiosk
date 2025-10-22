<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/api'

const router = useRouter()
const route = useRoute()

const pin = ref('')
const confirmPin = ref('')
const residentId = ref(null)
const hasPin = ref(false)
const isSettingPin = ref(false)

onMounted(async () => {
  residentId.value = route.query.resident_id
  if (!residentId.value) {
    alert('No user ID found. Please scan RFID again.')
    router.push('/login-rfid')
    return
  }

  // Check if user has PIN
  try {
    const res = await api.get(`/users/${residentId.value}/pin`)
    hasPin.value = res.data.has_pin
    isSettingPin.value = !hasPin.value   // <-- important: determine if setting PIN
    console.log('Has PIN:', hasPin.value, 'Is setting PIN:', isSettingPin.value)
  } catch (err) {
    console.error('❌ Failed to check PIN:', err)
    alert('Error checking PIN. Please try again.')
  }
})

const submitPin = async () => {
  if (!pin.value) return alert('Please enter a PIN')

  if (isSettingPin.value && pin.value !== confirmPin.value) {
    return alert('PINs do not match')
  }

  try {
    if (isSettingPin.value) {
      // Set new PIN
      await api.post(`/users/${residentId.value}/pin`, { pin: pin.value })
      alert('✅ PIN set successfully!')
    } else {
      // Verify existing PIN
      const res = await api.post(`/users/${residentId.value}/pin/verify`, { pin: pin.value })
      if (!res.data.valid) return alert('Invalid PIN')
    }

    router.push('/home')
  } catch (err) {
    console.error('❌ PIN error:', err)
    alert(err.response?.data?.detail || 'Error processing PIN')
  }
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex flex-col justify-center items-center font-poppins">
    <div class="bg-white w-[500px] h-[400px] rounded-lg shadow-2xl flex flex-col justify-center items-center p-8 gap-6">
      <h2 class="text-3xl font-semibold text-gray-700">
        {{ isSettingPin ? 'Set Your PIN' : 'Enter PIN' }}
      </h2>

      <input 
        type="password" 
        v-model="pin" 
        class="input input-bordered w-64 text-xl text-center" 
        placeholder="PIN" 
      />

      <input 
        v-if="isSettingPin" 
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
