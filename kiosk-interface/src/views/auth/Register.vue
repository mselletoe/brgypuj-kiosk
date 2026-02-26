<script setup>
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'

</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton/>
      <div class="flex justify-between items-center w-full">
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Register
          </h1>
          <p class="text-[#03335C] -mt-2">
            Register a new RFID for a resident.
          </p>
        </div>

        <h1 class="text-[#03335C] font-bold text-[45px]">0921843094</h1>
      </div>

    </div>

    <div class="flex flex-1 gap-8 w-full">
      <!-- Left Panel -->
      <div class="bg-white rounded-2xl shadow-lg p-6 flex-1 border border-gray-200 text-[#003A6B]">
        <p>Select a request transaction no.</p>

        <div class="grid grid-cols-4 mt-5 gap-6">
          <div class="text-[#B1202A] bg-red-50 rounded-xl shadow-sm px-4 py-3 border-2 border-red-200 text-center font-bold text-xl">
            <p>1232</p>
          </div>
        </div>
      </div>

      <!-- Right Panel -->
      <div class="flex flex-col text-[#003A6B] bg-[#EBF5FF] rounded-2xl shadow-lg p-6 w-[400px] border border-[#B0D7F8] text-center">
        <h2 class="font-bold text-2xl text-center">Resident Details</h2>
        <p class="italic text-[9px]">Please check the residents details before proceeding.</p>
        <div class="text-start mt-3">
          <p><span class="font-bold">Name:</span></p>
          <p><span class="font-bold">Birthdate:</span></p>
          <p><span class="font-bold">Address:</span></p>
        </div>
      </div>
    </div>

    <div class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0">
      <Button
        variant="outline"
        size="md"
      >
        Cancel
      </Button>
      <Button
        variant='secondary'
        size="md"
      >
        Submit
      </Button>
    </div>
  </div>
</template>
