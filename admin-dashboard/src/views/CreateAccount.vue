<script setup>
  /**
 * @file CreateAccount.vue
 * @description Administrative Account Registration Interface.
 * This component facilitates the promotion of an existing resident to an 
 * administrative role. It includes real-time password strength validation, 
 * credential matching, and dynamic resident fetching from the database.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NSelect, NInput, NSpin, useMessage, NIcon } from 'naive-ui'
import logo from '@/assets/logo.svg'
import { CheckmarkCircleOutline, CloseCircleOutline } from '@vicons/ionicons5'
import { registerAdmin, fetchResidentsDropdown } from '@/api/authService'

const router = useRouter()
const message = useMessage()

// --- Form State ---
const selectedResident = ref(null)
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loadingSubmit = ref(false)

// --- Data Fetching State ---
const residents = ref([])
const loadingResidents = ref(true)

/**
 * Initial component setup.
 * Fetches the list of residents to populate the "Staff Name" selection dropdown.
 */
onMounted(async () => {
  try {
    const res = await fetchResidentsDropdown()
    residents.value = res.map(r => ({ 
      label: r.full_name, 
      value: r.id 
    }))
  } catch (err) {
    message.error('Failed to load residents.')
    console.error(err)
  } finally {
    loadingResidents.value = false
  }
})

/**
 * Reactive password strength validation object.
 * Evaluates the current password string against organizational security requirements.
 */
const passValidation = computed(() => {
  return {
    minLength: password.value.length >= 8,
    hasNumber: /\d/.test(password.value),
    hasUpper: /[A-Z]/.test(password.value),
    hasLower: /[a-z]/.test(password.value)
  }
})

/**
 * Validates that the password and confirmation strings are identical.
 */
const passwordsMatch = computed(() => {
  return password.value === confirmPassword.value && password.value.length > 0
})

/**
 * Handles the administrative registration submission.
 * Validates requirements and invokes the remote registration service.
 */
const handleRegister = async () => {
  const { minLength, hasNumber, hasUpper, hasLower } = passValidation.value

  // 1. Check for empty fields
  if (!selectedResident.value || !username.value || !password.value || !confirmPassword.value) {
    message.error('Please fill out all fields.')
    return
  }

  // 2. Enforce complexity requirements
  if (!minLength || !hasNumber || !hasUpper || !hasLower) {
    message.error('Password does not meet requirements.')
    return
  }

  // 3. Verify credential matching
  if (!passwordsMatch.value) {
    message.error('Passwords do not match.')
    return
  }

  loadingSubmit.value = true

  try {
    // 4. Submit to Backend Service
    await registerAdmin({
      resident_id: selectedResident.value,
      username: username.value,
      password: password.value,
      role: 'Admin'
    })

    message.success('Account created successfully!')
    // 5. Navigate to Dashboard Overview
    router.push('/overview')
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to create account'
    message.error(errorMsg)
  } finally {
    loadingSubmit.value = false
  }
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
      <div class="flex justify-between mb-7 w-full">
        <div class="text-[#013C6D] text-start">
          <h2 class="text-2xl font-bold">Create Account</h2>
          <p class="text-sm">
            Already have an account?
            <router-link
              to="/auth"
              class="text-sm text-[#0957FF] font-bold hover:underline"
            >
              Login
            </router-link>
          </p>
        </div>
        <img :src="logo" alt="Logo" class="w-[80px]" />
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5 w-full">
        <NSelect
          v-model:value="selectedResident"
          :options="residents"
          placeholder="Select Resident (Staff Name)"
          size="large"
          filterable
          :loading="loadingResidents"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

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

        <!-- Password rules -->
        <div v-if="password.length > 0" class="text-left pl-3 bg-white/50 rounded-md space-y-1">
          <div v-for="(valid, key) in passValidation" :key="key" class="flex items-center py-1">
            <NIcon size="16" :color="valid ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="valid" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span
              :class="['ml-2 text-xs', valid ? 'text-green-600' : 'text-red-500']"
            >
              {{
                key === 'minLength' ? 'At least 8 characters' :
                key === 'hasUpper' ? 'One uppercase letter (A-Z)' :
                key === 'hasLower' ? 'One lowercase letter (a-z)' :
                'One number (0-9)'
              }}
            </span>
          </div>
        </div>

        <NInput
          v-model:value="confirmPassword"
          type="password"
          placeholder="Confirm Password"
          size="large"
          show-password-on="click"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <div v-if="confirmPassword.length > 0" class="text-left pl-3">
          <div class="flex items-center">
            <NIcon size="16" :color="passwordsMatch ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passwordsMatch" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span
              :class="['ml-2 text-xs', passwordsMatch ? 'text-green-600' : 'text-red-500']"
            >
              {{ passwordsMatch ? 'Passwords match' : 'Passwords mismatch' }}
            </span>
          </div>
        </div>

        <div class="pt-3">
          <button
            type="submit"
            :disabled="loadingSubmit"
            class="w-full bg-[#013C6D] h-[42px] text-white font-semibold py-2 rounded-md
                   transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)]
                   flex items-center justify-center"
          >
            <NSpin v-if="loadingSubmit" size="small" stroke="white" />
            <span v-else>Create Account</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>