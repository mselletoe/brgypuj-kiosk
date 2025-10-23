<script setup>
import { PhoneIcon, ChatBubbleBottomCenterTextIcon, HomeIcon, InformationCircleIcon } from '@heroicons/vue/24/outline';
</script>

<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="bg-[#FFF0F1] border border-[#FFD5D8] rounded-xl shadow px-6 py-3 text-[#D32F2F] flex flex-col items-center pb-4">
      <div class="flex justify-center items-center gap-2 mb-2 pt-[32px]">
        <PhoneIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Emergency</h3>
      </div>
      <p class="text-7xl font-bold mb-1">911</p>
      <p class="text-sm">For life-threatening emergencies</p>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3">
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <ChatBubbleBottomCenterTextIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Barangay Office</h3>
      </div>
      <div class="space-y-2 text-gray-700">
        <div>
          <span class="font-semibold block">Phone</span>
          <span>(046) 123-4567</span>
        </div>
        <div>
          <span class="font-semibold block">Email</span>
          <span>poblacion1.amadeo@gmail.com</span>
        </div>
        <div>
          <span class="font-semibold block">Office Hours</span>
          <span>Monday to Friday, 8:00 AM - 5:00 PM</span>
        </div>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 col-span-1">
       <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <HomeIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Visit Us</h3>
      </div>
      <div class="text-gray-700">
        <span class="font-semibold block">Address</span>
        <span>Brgy. Poblacion I, Amadeo, Cavite</span>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 col-span-1">
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <InformationCircleIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Technical Support</h3>
      </div>
      <p class="text-gray-700">
        If you're experiencing issues with the kiosk, please contact our office or visit during business hours for assistance.
      </p>
    </div>
  </div>
</template>