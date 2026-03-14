<script setup>
import { NConfigProvider, NMessageProvider } from 'naive-ui'
import { blueThemeOverrides } from './assets/theme.js'
import { useWebSocket } from '@/composables/useWebSocket'

const { connect } = useWebSocket()
connect() 
</script>

<template>
  <n-config-provider :theme-overrides="blueThemeOverrides">
    <n-message-provider>
      <router-view />
    </n-message-provider>
  </n-config-provider>
</template>