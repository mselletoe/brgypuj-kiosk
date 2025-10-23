<script setup>
import { ref } from 'vue'
import { NInput } from 'naive-ui'
import logo from '@/assets/logo.svg'
import { useRouter } from 'vue-router'
import { useAuth } from '@/stores/authStore'
import { loginStaff } from '@/api/authApi'

const email = ref('')
const password = ref('')
const router = useRouter()
const auth = useAuth()

async function handleLogin() {
  try {
    const res = await loginStaff(email.value, password.value)
    auth.setToken(res.access_token)
    console.log('Login successful!', auth.user)
    router.push('/overview')
  } catch (err) {
    console.error(err.response?.data?.detail || 'Login failed')
  }
}
</script>

<template>
  <div class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)] flex items-center justify-center">
    <div class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem] text-center flex flex-col items-center justify-center">
      <div class="mb-7">
        <img :src="logo" alt="Logo" class="w-[150px]" />
      </div>

      <form @submit.prevent="handleLogin" class="space-y-7 w-full max-w-md">
        <NInput
          v-model:value="email"
          type="email"
          placeholder="Email"
          size="large"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />
        <NInput
          v-model:value="password"
          type="password"
          placeholder="Password"
          size="large"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <button
          type="submit"
          class="w-full bg-[#0957FF] h-[42px] text-white font-semibold py-2 rounded-md 
                 hover:bg-[#0957FF]-500 transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
        >
          Login
        </button>

        <hr class="my-6 border-gray-300" />

        <button
            type="button"
            class="w-full bg-[#013C6D] h-[42px] text-white font-semibold py-2 rounded-md 
             transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
        >
            Create Account
        </button>
      </form>
    </div>
  </div>
</template>