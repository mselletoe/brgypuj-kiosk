<template>
  <div class="drawer drawer-open py-6 px-8">
    <div class="drawer-side">
      <ul class="menu text-base-content w-full h-full space-y-1 text-sm">
        <li>
          <router-link
            to="/overview"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/overview',
              'text-[#535353]': route.path !== '/overview'
            }"
          >
            Overview
          </router-link>
        </li>

        <li>
          <router-link
            to="/requests"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/requests',
              'text-[#535353]': route.path !== '/requests'
            }"
          >
            Requests
          </router-link>
        </li>

        <li>
          <router-link
            to="/document-templates"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/document-templates',
              'text-[#535353]': route.path !== '/document-templates'
            }"
          >
            Document Templates
          </router-link>
        </li>

        <li>
          <router-link
            to="/announcements"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/announcements',
              'text-[#535353]': route.path !== '/announcements'
            }"
          >
            Announcements
          </router-link>
        </li>

        <li>
          <router-link
            to="/appointments"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/appointments',
              'text-[#535353]': route.path !== '/appointments'
            }"
          >
            Appointments
          </router-link>
        </li>

        <li>
          <router-link
            to="/community-feedback"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/community-feedback',
              'text-[#535353]': route.path !== '/community-feedback'
            }"
          >
            Community Feedback
          </router-link>
        </li>

        <li>
          <router-link
            to="/information-hub"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/information-hub',
              'text-[#535353]': route.path !== '/information-hub'
            }"
          >
            Information Hub
          </router-link>
        </li>

        <li>
          <router-link
            to="/residents"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/residents',
              'text-[#535353]': route.path !== '/residents'
            }"
          >
            Residents
          </router-link> 
        </li>

        <li>
          <router-link
            to="/utilities"
            class="block w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/utilities',
              'text-[#535353]': route.path !== '/utilities'
            }"
          >
            Utilities
          </router-link> 
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>
