<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import logo from '@/assets/logo.svg'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''

  if (!email.value || !password.value) {
    errorMessage.value = 'Please enter email and password'
    return
  }

  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/auth/login',
      { email: email.value, password: password.value },
      { withCredentials: true } // ensures cookies if needed
    )
    console.log('✅ Logged in successfully:', res.data)

    localStorage.setItem('staff', JSON.stringify(res.data))
    router.push('/overview')
  } catch (err) {
    console.error('❌ Login failed:', err)
    errorMessage.value = err.response?.data?.detail || 'Login failed'
  }
}
</script>

<template>
  <div
    class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)] flex items-center justify-center"
  >
    <div
      class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem] text-center flex flex-col items-center justify-center"
    >
      <img :src="logo" alt="Logo" class="w-60 mb-10" />

      <form @submit.prevent="handleLogin" class="space-y-6 w-full max-w-md">
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full px-4 py-2 rounded-md bg-white text-black
                 placeholder-[#ADADAD] focus:outline-none focus:ring-2 focus:ring-[#0957FF]/50 shadow-md"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full px-4 py-2 rounded-md bg-white text-black
                 placeholder-[#ADADAD] focus:outline-none focus:ring-2 focus:ring-[#0957FF]/50 shadow-md"
        />
        <button
          type="submit"
          class="w-full bg-[#013C6D] text-white font-semibold py-2 rounded-md
                 hover:bg-[#012C50] transition shadow-md"
        >
          Login
        </button>
        <p v-if="errorMessage" class="text-red-600 mt-2 text-sm">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>