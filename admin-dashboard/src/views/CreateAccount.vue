<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NSelect, NInput, NSpin, useMessage, NIcon } from 'naive-ui'
import logo from '@/assets/logo.svg'
import { useAuth } from '@/stores/authStore'
import { CheckmarkCircleOutline, CloseCircleOutline } from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const auth = useAuth()

// Form state
const selectedResident = ref(null)
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loadingSubmit = ref(false)

// State for dropdowns
const residents = ref([])
const loadingResidents = ref(true)

// Fetch available residents when the component mounts
onMounted(async () => {
  try {
    const data = await getAvailableResidents()
    // Format the data for the NSelect component
    residents.value = data.map(res => ({
      label: `${res.first_name} ${res.middle_name || ''} ${res.last_name}`,
      value: res.id
    }))
  } catch (err) {
    console.error('Failed to fetch residents:', err)
    message.error('Failed to load available residents.')
  } finally {
    loadingResidents.value = false
  }
})

// Password validation state
const passValidation = computed(() => {
  const minLength = password.value.length >= 8
  const hasNumber = /\d/.test(password.value)
  const hasUpper = /[A-Z]/.test(password.value)
  const hasLower = /[a-z]/.test(password.value)
  return { minLength, hasNumber, hasUpper, hasLower }
})

const passwordsMatch = computed(() => {
  return password.value === confirmPassword.value && password.value.length > 0
})

async function handleRegister() {
  // 1. Validation
  const { minLength, hasNumber, hasUpper, hasLower } = passValidation.value
  if (!selectedResident.value || !email.value || !password.value || !confirmPassword.value) {
    message.error('Please fill out all fields.')
    return
  }
  if (!minLength || !hasNumber || !hasUpper || !hasLower) {
    message.error('Please ensure your password meets all requirements.')
    return
  }
  if (!passwordsMatch.value) {
    message.error('Passwords do not match.')
    return
  }

  // 2. Set loading state
  loadingSubmit.value = true

  // 3. Prepare payload
  const payload = {
    resident_id: selectedResident.value,
    email: email.value,
    password: password.value,
    role: "Admin" 
  }

  // 4. Call API
  try {
    // Step 1: Register the account
    await registerStaff(payload)
    
    // Step 2: Log in with the new account
    try {
      const loginRes = await loginStaff(email.value, password.value)
      auth.setToken(loginRes.access_token)
      message.success('Account created and logged in successfully!')
      router.push('/overview')
    } catch (loginErr) {
      console.error('Login after registration failed:', loginErr)
      message.error('Account created, but auto-login failed. Please log in manually.')
      router.push('/auth')
    }

  } catch (regErr) {
    // Handle registration error
    console.error('Registration failed:', regErr)
    const errorMessage = regErr.response?.data?.detail || 'An unknown error occurred.'
    message.error(`Registration failed: ${errorMessage}`)
  } finally {
    // 5. Unset loading state
    loadingSubmit.value = false
  }
}
</script>

<template>
  <div class="h-screen w-screen bg-[linear-gradient(to_bottom_right,_#3291E3,_#FFFFFF,_#C3EAFF)] flex items-center justify-center">
    <div class="backdrop-blur-md bg-white/20 p-10 rounded-2xl shadow-2xl w-[30rem] text-center flex flex-col items-center justify-center">
      <div class="flex justify-between mb-7 w-full">
        <div class="text-[#013C6D] text-start">
            <h2 class="text-2xl font-bold">Create Account</h2>
            <p class="text-sm">
              Already have an account? 
              <router-link to="/auth" class="text-sm text-[#0957FF] font-bold hover:underline">
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
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
          size="large"
          filterable
          :loading="loadingResidents"
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
          show-password-on="click"
          class="text-left shadow-[4px_4px_10px_rgba(128,128,128,0.15)]"
        />

        <div v-if="password.length > 0" class="text-left pl-3 bg-white/50 rounded-md space-y-1"> <div class="flex items-center py-1"> <NIcon size="16" :color="passValidation.minLength ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passValidation.minLength" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span :class="['ml-2 text-xs', passValidation.minLength ? 'text-green-600' : 'text-red-500']">
              At least 8 characters
            </span>
          </div>
          <div class="flex items-center py-1">
            <NIcon size="16" :color="passValidation.hasUpper ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passValidation.hasUpper" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span :class="['ml-2 text-xs', passValidation.hasUpper ? 'text-green-600' : 'text-red-500']">
              One uppercase letter (A-Z)
            </span>
          </div>
          <div class="flex items-center py-1">
            <NIcon size="16" :color="passValidation.hasLower ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passValidation.hasLower" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span :class="['ml-2 text-xs', passValidation.hasLower ? 'text-green-600' : 'text-red-500']">
              One lowercase letter (a-z)
            </span>
          </div>
          <div class="flex items-center py-1">
            <NIcon size="16" :color="passValidation.hasNumber ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passValidation.hasNumber" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span :class="['ml-2 text-xs', passValidation.hasNumber ? 'text-green-600' : 'text-red-500']">
              One number (0-9)
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

        <div v-if="confirmPassword.length > 0" class="text-left pl-3"> <div class="flex items-center">
            <NIcon size="16" :color="passwordsMatch ? '#22c55e' : '#ef4444'">
              <CheckmarkCircleOutline v-if="passwordsMatch" />
              <CloseCircleOutline v-else />
            </NIcon>
            <span :class="['ml-2 text-xs', passwordsMatch ? 'text-green-600' : 'text-red-500']">
              {{ passwordsMatch ? 'Passwords match' : 'Passwords mismatch' }} </span>
          </div>
        </div>
        
        <div class="pt-3"> 
            <button 
              type="submit" 
              class="w-full bg-[#013C6D] h-[42px] text-white font-semibold py-2 rounded-md transition shadow-[4px_4px_10px_rgba(128,128,128,0.25)] flex items-center justify-center"
              :disabled="loadingSubmit"
            >
              <NSpin v-if="loadingSubmit" size="small" stroke="white" />
              <span v-else>Create Account</span>
            </button>
        </div>
      </form>
    </div>
  </div>
</template>