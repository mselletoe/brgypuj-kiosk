<script setup>
import PageTitle from '@/components/shared/PageTitle.vue'
import ResidentsTable from '@/components/ResidentsTable.vue'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/solid'
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])
const query = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  if (val !== query.value) query.value = val
})
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full">
    <header class="flex items-center justify-between mb-6">
      <PageTitle title="Residents" />
      <label class="input input-bordered flex items-center gap-2 bg-[#F3F3F3] py-1 px-2 rounded-md w-[300px]">
        <MagnifyingGlassIcon class="h-5 w-5 opacity-50" />
        <input
          type="search"
          class="grow bg-transparent outline-none"
          placeholder="Search"
          v-model="query"
          @input="$emit('update:modelValue', query)"
        />
      </label>
      <!--FILTERS-->
    </header>
    
    <ResidentsTable />
  </div>
</template>