<script setup>
  /**
 * @file views/auth/CreateAccount.vue
 * @description Admin account registration view. Promotes an existing resident
 * to an admin role with real-time password validation and resident dropdown.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NSelect, NInput, NSpin, useMessage, NIcon } from 'naive-ui'
import logo from '@/assets/logo.png'
import { CheckmarkCircleOutline, CloseCircleOutline } from '@vicons/ionicons5'
import { registerAdmin, fetchResidentsDropdown } from '@/api/authService'

const router = useRouter()
const message = useMessage()
const selectedResident = ref(null)
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loadingSubmit = ref(false)
const residents = ref([])
const loadingResidents = ref(true)

// =================================================================================
// Fetch residents on mount to populate the staff name dropdown.
// =================================================================================
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

// =================================================================================
// Evaluates the current password against complexity requirements.
// =================================================================================
const passValidation = computed(() => {
  return {
    minLength: password.value.length >= 8,
    hasNumber: /\d/.test(password.value),
    hasUpper: /[A-Z]/.test(password.value),
    hasLower: /[a-z]/.test(password.value)
  }
})

const passwordsMatch = computed(() => {
  return password.value === confirmPassword.value && password.value.length > 0
})

// =================================================================================
// Handles the registration form submission.
// =================================================================================
const handleRegister = async () => {
  const { minLength, hasNumber, hasUpper, hasLower } = passValidation.value

  // Guard: ensure all fields are filled before proceeding
  if (!selectedResident.value || !username.value || !password.value || !confirmPassword.value) {
    message.error('Please fill out all fields.')
    return
  }

  // Guard: enforce password complexity requirements
  if (!minLength || !hasNumber || !hasUpper || !hasLower) {
    message.error('Password does not meet requirements.')
    return
  }

  // Guard: confirm both password fields are identical
  if (!passwordsMatch.value) {
    message.error('Passwords do not match.')
    return
  }

  loadingSubmit.value = true

  try {
    await registerAdmin({
      resident_id: selectedResident.value,
      username: username.value,
      password: password.value,
      role: 'Admin'
    })

    message.success('Account created successfully!')
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
  <div class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)]
           flex items-center justify-center">

    <!-- Glassmorphism card -->
    <div class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem]
             text-center flex flex-col items-center justify-center">

      <!-- Header: title, login link, and brand logo -->
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

      <!-- Registration form -->
      <form @submit.prevent="handleRegister" class="space-y-5 w-full">

        <!-- Resident dropdown — filterable, loads async from API -->
        <NSelect
          v-model:value="selectedResident"
          :options="residents"
          placeholder="Select Resident (Staff Name)"
          size="large"
          filterable
          :loading="loadingResidents"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <!-- Credential fields -->
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

        <!-- Password strength rules — shown only while typing -->
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

        <!-- Confirm password field -->
        <NInput
          v-model:value="confirmPassword"
          type="password"
          placeholder="Confirm Password"
          size="large"
          show-password-on="click"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <!-- Confirm password match indicator — shown only while typing -->
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

        <!-- Submit button — shows spinner during request -->
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