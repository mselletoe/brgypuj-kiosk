<script setup>
import {
  HomeIcon,
  DocumentTextIcon,
  BellIcon,
  CalendarDaysIcon,
  UsersIcon,
  ChatBubbleBottomCenterTextIcon,
  FolderIcon,
  Cog6ToothIcon,
  DocumentCheckIcon 
} from '@heroicons/vue/24/solid'
</script>

<template>
  <div class="drawer drawer-open ">
    <div class="drawer-side">
      <ul class="menu text-base-content w-full h-full space-y-1 text-sm">

        <li>
          <router-link
            to="/overview"
            class="flex items-center gap-3 w-full py-3 px-4 rounded-md text-[#535353]"
          >
            <HomeIcon class="w-5 h-5" />
            Overview
          </router-link>
        </li>

        <li>
          <router-link
            to="/requests"
            class="flex items-center gap-3 w-full py-3 px-4 rounded-md text-[#535353]"
          >
            <DocumentTextIcon class="w-5 h-5" />
            Requests
          </router-link>
        </li>

        <li>
          <router-link
            to="/document-templates"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <FolderIcon class="w-5 h-5" />
            Document Templates
          </router-link>
        </li>

        <li>
          <router-link
            to="/announcements"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <BellIcon class="w-5 h-5" />
            Announcements
          </router-link>
        </li>

        <li>
          <router-link
            to="/appointments"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <CalendarDaysIcon class="w-5 h-5" />
            Appointments
          </router-link>
        </li>

        <li>
          <router-link
            to="/community-feedback"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <ChatBubbleBottomCenterTextIcon class="w-5 h-5" />
            Community Feedback
          </router-link>
        </li>

        <li>
          <router-link
            to="/information-hub"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <Cog6ToothIcon class="w-5 h-5" />
            Information Hub
          </router-link>
        </li>

        <li>
          <router-link
            to="/residents"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <UsersIcon class="w-5 h-5" />
            Residents
          </router-link> 
        </li>

        <li>
          <router-link
            to="/equipment-management"
            class="flex items-center gap-3 w-full py-3 px-4 font-normal rounded-md text-[#535353]"
          >
            <DocumentCheckIcon class="w-5 h-5" />
            Equipment Request Management
          </router-link> 
        </li>

      </ul>
    </div>
  </div>
</template>

<style scoped>
.router-link-active {
  background-color: #0957FF;
  color: white;
  font-weight: 600; 
}
</style>