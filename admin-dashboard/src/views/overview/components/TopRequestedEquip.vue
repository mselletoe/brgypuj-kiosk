<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getEquipmentInventory } from "@/api/equipmentService";

const props = defineProps({
  equipsList: { type: Array, required: true },
});

const router = useRouter();
const inventoryMap = ref({}); // item_name -> available count

onMounted(async () => {
  try {
    const response = await getEquipmentInventory();
    const data = response.data || response || [];
    data.forEach((item) => {
      // inventory uses item.name and item.available_quantity
      inventoryMap.value[item.name] = item.available_quantity ?? 0;
    });
  } catch (e) {
    console.error("Failed to load inventory for TopRequestedEquip", e);
  }
});

const topEquips = computed(() => {
  const counts = {};
  props.equipsList.forEach((e) => {
    if (e.items && e.items.length > 0) {
      e.items.forEach((item) => {
        const name = item.item_name || "Unknown";
        if (!counts[name]) counts[name] = 0;
        counts[name] += item.quantity || 1;
      });
    }
  });

  return Object.entries(counts)
    .map(([name, requests]) => ({
      name,
      requests,
      available: inventoryMap.value[name] ?? null,
    }))
    .sort((a, b) => b.requests - a.requests)
    .slice(0, 4);
});
</script>

<template>
  <div
    class="bg-white rounded-[24px] p-8 shadow-sm border border-gray-100 flex flex-col h-full"
  >
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-800 tracking-tight">
          Top Requested Equipment
        </h2>
        <p
          class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
        >
          By item name
        </p>
      </div>
      <button
        @click="router.push('/equipment-inventory')"
        class="text-[11px] font-bold text-blue-600 uppercase tracking-widest hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg"
      >
        Manage
      </button>
    </div>

    <div
      v-if="topEquips.length === 0"
      class="text-sm text-gray-400 text-center mt-6"
    >
      No equipment data available.
    </div>

    <div class="grid grid-cols-2 gap-3 flex-1">
      <div
        v-for="(item, i) in topEquips"
        :key="item.name"
        class="equip-card border border-gray-100 rounded-[16px] p-4 flex flex-col gap-2 bg-gray-50 hover:bg-white hover:shadow-sm transition-all duration-300"
        :style="{ animationDelay: `${0.1 + i * 0.07}s` }"
      >
        <span class="text-sm font-bold text-gray-800 leading-tight">{{
          item.name
        }}</span>
        <div class="flex items-center justify-between mt-auto">
          <span class="text-xs text-gray-500">
            <span class="font-black text-gray-700">{{ item.requests }}</span>
            requests
          </span>
          <span
            v-if="item.available !== null"
            class="text-[11px] font-bold px-2 py-0.5 rounded-full"
            :class="
              item.available > 1
                ? 'text-green-600 bg-green-50'
                : 'text-amber-600 bg-amber-50'
            "
          >
            {{ item.available }} available
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.equip-card {
  opacity: 0;
  animation: cardPop 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes cardPop {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(6px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
