<script setup>
/**
 * @file Auth.vue
 * @description Admin authentication view providing login functionality
 * and navigation to account creation.
 */
import { ref } from 'vue'
import { NInput, useMessage } from 'naive-ui'
import logo from '@/assets/logo.png'
import { useRouter } from 'vue-router'
import { loginAdmin } from '@/api/authService'
import { useAdminAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const message = useMessage()
const adminAuth = useAdminAuthStore()

/**
 * Handles the login form submission. Validates that both fields are filled,
 * calls the login API, initializes the admin session with the returned access
 * token, and redirects to the overview page on success.
 */
const handleLogin = async () => {
  if (!username.value || !password.value) {
    message.warning('Please enter your username and password.')
    return
  }

  loading.value = true

  try {
    const data = await loginAdmin(username.value, password.value)
    await adminAuth.initSession(data.access_token)
    message.success('Login successful')
    router.push('/overview')
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Invalid username or password'
    message.error(errorMsg)
  } finally {
    loading.value = false
  }
}

/** Navigates the user to the account creation page. */
function goToCreateAccount() {
  router.push('/create-account')
}
</script>

<template>
  <div class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)] flex items-center justify-center">
    <!-- Glassmorphism login card -->
    <div class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem]
          text-center flex flex-col items-center justify-center">

      <!-- Logo -->
      <div class="mb-7">
        <img :src="logo" alt="Logo" class="w-[150px]" />
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-7 w-full max-w-md">
        <!-- Username -->
        <NInput
          v-model:value="username"
          type="text"
          placeholder="Username"
          size="large"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <!-- Password -->
        <NInput
          v-model:value="password"
          type="password"
          placeholder="Password"
          size="large"
          show-password-on="click"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <!-- Button: Login -->
        <button
          type="submit"
          class="w-full bg-[#0957FF] h-[42px] text-white font-semibold py-2 rounded-md
                 transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]"
          :disabled="loading"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <hr class="my-6 border-gray-300" />

        <!-- Button: Create Account -->
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