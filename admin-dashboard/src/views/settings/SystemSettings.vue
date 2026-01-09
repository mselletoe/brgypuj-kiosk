<script setup>
import { ref } from 'vue'

const isBackingUp = ref(false)
const backupMessage = ref(null)

const handleBackup = async () => {
  isBackingUp.value = true
  backupMessage.value = null

  try {
    const response = await api.post('/backup/run', {}, {
      responseType: 'blob' // important to receive the file
    })

    const blob = new Blob([response.data], { type: 'application/octet-stream' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `backup_${new Date().toISOString().slice(0,19)}.dump`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    backupMessage.value = {
      type: 'success',
      text: 'Backup created and downloaded successfully!'
    }

  } catch (err) {
    backupMessage.value = {
      type: 'error',
      text: `Backup failed: ${err.message}`
    }
  } finally {
    isBackingUp.value = false
  }
}
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen space-y-6">
    <button
      @click="handleBackup"
      :disabled="isBackingUp"
      class="w-full py-3 px-6 bg-blue-600 text-white font-bold rounded-lg shadow hover:bg-blue-700 transition"
    >
      <span v-if="isBackingUp">Backing up...</span>
      <span v-else>Backup Now</span>
    </button>

    <div v-if="backupMessage" class="mt-4 p-3 rounded-md"
      :class="backupMessage.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
      {{ backupMessage.text }}
    </div>
  </div>
</template>
