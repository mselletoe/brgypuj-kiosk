<script setup>
  /**
 * @file Auth.vue
 * @description Administrative Authentication Gateway.
 * Provides the primary login interface for the Admin Dashboard.
 * Handles credential validation, JWT acquisition via the auth service,
 * and session initialization within the global Pinia store.
 */
import { ref } from 'vue'
import { NInput, useMessage } from 'naive-ui'
import logo from '@/assets/logo.svg'
import { useRouter } from 'vue-router'
import { loginAdmin } from '@/api/authService'
import { useAdminAuthStore } from '@/stores/auth'

// --- State Management ---
const username = ref('')
const password = ref('')
const loading = ref(false)

// --- Composition Utilities ---
const router = useRouter()
const message = useMessage()
const adminAuth = useAdminAuthStore()

/**
 * Orchestrates the administrative login process.
 * Validates local input, performs remote authentication, 
 * and handles UI feedback for success or failure states.
 */
const handleLogin = async () => {
  // 1. Basic Client-Side Validation
  if (!username.value || !password.value) {
    message.warning('Please enter your username and password.')
    return
  }

  loading.value = true

  try {
    // 2. Request JWT from Backend Service
    const data = await loginAdmin(username.value, password.value)

    // 3. Initialize Session: Store token and basic user metadata
    // This triggers the persist() logic to save the token to LocalStorage
    adminAuth.setAuth(data.access_token, { username: username.value })

    message.success('Login successful')

    // 4. Redirect to the Dashboard Overview
    router.push('/overview')
  } catch (err) {
    // 5. Error Handling: Extract backend detail or provide generic fallback
    const errorMsg = err.response?.data?.detail || 'Invalid username or password'
    message.error(errorMsg)
  } finally {
    loading.value = false
  }
}

/**
 * Navigates to the administrative registration flow.
 */
function goToCreateAccount() {
  router.push('/create-account')
}
</script>

<template>
  <div
    class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)]
           flex items-center justify-center"
  >
    <div
      class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem]
             text-center flex flex-col items-center justify-center"
    >
      <div class="mb-7">
        <img :src="logo" alt="Logo" class="w-[150px]" />
      </div>

      <form @submit.prevent="handleLogin" class="space-y-7 w-full max-w-md">
        <NInput
          v-model:value="username"
          type="text"
          placeholder="Username"
          size="large"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <NInput
          v-model:value="password"
          type="password"
          placeholder="Password"
          size="large"
          show-password-on="click"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <button
          type="submit"
          class="w-full bg-[#0957FF] h-[42px] text-white font-semibold py-2 rounded-md
                 transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
          :disabled="loading"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <hr class="my-6 border-gray-300" />

        <button
          type="button"
          @click="goToCreateAccount"
          class="w-full bg-[#013C6D] h-[42px] text-white font-semibold py-2 rounded-md
                 transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
        >
          Create Account
        </button>
      </form>
    </div>
  </div>
</template>
