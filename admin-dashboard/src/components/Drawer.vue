<script setup>
import { useRoute } from 'vue-router'
import {
  HomeIcon,
  DocumentTextIcon,
  BellIcon,
  CalendarDaysIcon,
  UsersIcon,
  ChatBubbleBottomCenterTextIcon,
  FolderIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/solid'

const route = useRoute()
</script>

<template>
  <div class="drawer drawer-open ">
    <div class="drawer-side">
      <ul class="menu text-base-content w-full h-full space-y-1 text-sm">
        <li>
          <router-link
            to="/overview"
            class="flex items-center gap-3 w-full py-3 px-4 rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/overview',
              'text-[#535353]': route.path !== '/overview'
            }"
          >
            <HomeIcon class="w-5 h-5" />
            Overview
          </router-link>
        </li>

        <li>
          <router-link
            to="/requests"
            class="flex items-center gap-3 w-full py-3 px-4 rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/requests',
              'text-[#535353]': route.path !== '/requests'
            }"
          >
            <DocumentTextIcon class="w-5 h-5" />
            Requests
          </router-link>
        </li>

        <li>
          <router-link
            to="/document-templates"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/document-templates',
              'text-[#535353]': route.path !== '/document-templates'
            }"
          >
            <FolderIcon class="w-5 h-5" />
            Document Templates
          </router-link>
        </li>

        <li>
          <router-link
            to="/announcements"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/announcements',
              'text-[#535353]': route.path !== '/announcements'
            }"
          >
            <BellIcon class="w-5 h-5" />
            Announcements
          </router-link>
        </li>

        <li>
          <router-link
            to="/appointments"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/appointments',
              'text-[#535353]': route.path !== '/appointments'
            }"
          >
            <CalendarDaysIcon class="w-5 h-5" />
            Appointments
          </router-link>
        </li>

        <li>
          <router-link
            to="/community-feedback"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/community-feedback',
              'text-[#535353]': route.path !== '/community-feedback'
            }"
          >
            <ChatBubbleBottomCenterTextIcon class="w-5 h-5" />
            Community Feedback
          </router-link>
        </li>

        <li>
          <router-link
            to="/information-hub"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/information-hub',
              'text-[#535353]': route.path !== '/information-hub'
            }"
          >
            <Cog6ToothIcon class="w-5 h-5" />
            Information Hub
          </router-link>
        </li>

        <li>
          <router-link
            to="/residents"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/residents',
              'text-[#535353]': route.path !== '/residents'
            }"
          >
            <UsersIcon class="w-5 h-5" />
            Residents
          </router-link> 
        </li>

        <li>
          <router-link
            to="/utilities"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md"
            :class="{
              'bg-[#0957FF] text-white font-semibold': route.path === '/utilities',
              'text-[#535353]': route.path !== '/utilities'
            }"
          >
            <Cog6ToothIcon class="w-5 h-5" />
            Utilities
          </router-link> 
        </li>
      </ul>
    </div>
  </div>
</template>