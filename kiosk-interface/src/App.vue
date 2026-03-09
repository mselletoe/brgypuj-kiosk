<script setup>
import { useAutoLogout } from '@/composables/useAutoLogout'
useAutoLogout()
</script>

<template>
  <router-view />
</template>