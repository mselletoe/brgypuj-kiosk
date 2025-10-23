<script setup>
import { ref } from 'vue'
import { NSelect, NInput } from 'naive-ui'
import logo from '@/assets/logo.svg'

const selectedResident = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const residents = [
  { label: 'Resident 1', value: 'resident1' },
  { label: 'Resident 2', value: 'resident2' },
  { label: 'Resident 3', value: 'resident3' }
]

function handleLogin() {
  console.log('Creating account with:', {
    selectedResident: selectedResident.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value
  })
}
</script>

<template>
  <div class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)] flex items-center justify-center">
    <div class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem] text-center flex flex-col items-center justify-center">
      <div class="flex justify-between mb-7 w-full">
        <div class="text-[#013C6D] text-start">
            <h2 class="text-2xl font-bold">Create Account</h2>
            <p class="text-sm">Already have an account? <span class="text-sm text-[#0957FF] font-bold">Login</span></p>
        </div>
        <img :src="logo" alt="Logo" class="w-[80px]" />
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5 w-full">
        <NSelect
          v-model:value="selectedResident"
          :options="residents"
          placeholder="Select Resident"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
          size="large"
        />
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
        <NInput
          v-model:value="password"
          type="password"
          placeholder="Confirm Password"
          size="large"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />
        <div class="pt-3"> 
            <button 
            type="button" 
            class="w-full bg-[#013C6D] h-[42px] text-white font-semibold py-2 rounded-md transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
            >
            Create Account
            </button>
        </div>
      </form>
    </div>
  </div>
</template>