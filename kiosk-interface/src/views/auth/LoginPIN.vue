<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { disableTouchToStart } from '@/composables/touchToStart'

const router = useRouter()
const pin = ref('')

// Sample code ko lang 'to while re-routing kanina. So you can replace this with your code na.
// But make sure to take note of this block sa baba.

const submitPin = () => {
  if (pin.value === '1234') {
    disableTouchToStart()
    router.push('/home')
  } else {
    alert('Invalid PIN')
  }
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex flex-col justify-center items-center font-poppins">
    <div class="bg-white w-[500px] h-[350px] rounded-lg shadow-2xl flex flex-col justify-center items-center p-8 gap-6">
      <h2 class="text-3xl font-semibold text-gray-700">Enter PIN</h2>
      <input type="password" v-model="pin" class="input input-bordered w-64 text-xl text-center" placeholder="PIN" />
      <button @click="submitPin" class="btn btn-primary w-64 h-16 text-2xl">Submit</button>
    </div>
  </div>
</template>