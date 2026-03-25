<script setup>
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronDownIcon } from "@heroicons/vue/24/outline";
import Button from "@/components/shared/Button.vue";

const props = defineProps({
  selectedResident: Object,
  verifyMonth: String,
  verifyDay: String,
  verifyYear: String,
  verificationError: String,
  isVerifying: Boolean,
});

const emit = defineEmits([
  "update:verifyMonth",
  "update:verifyDay",
  "update:verifyYear",
  "verify",
  "close",
]);

const { t } = useI18n();

const months = [
  { name: "January", value: "01" },
  { name: "February", value: "02" },
  { name: "March", value: "03" },
  { name: "April", value: "04" },
  { name: "May", value: "05" },
  { name: "June", value: "06" },
  { name: "July", value: "07" },
  { name: "August", value: "08" },
  { name: "September", value: "09" },
  { name: "October", value: "10" },
  { name: "November", value: "11" },
  { name: "December", value: "12" },
];

const days = Array.from({ length: 31 }, (_, i) =>
  (i + 1).toString().padStart(2, "0"),
);
const currentYear = new Date().getFullYear();
const years = Array.from({ length: currentYear - 1899 }, (_, i) =>
  (currentYear - i).toString(),
);

const showMonthDropdown = ref(false);
const showDayDropdown = ref(false);
const showYearDropdown = ref(false);

function toggle(menu) {
  showMonthDropdown.value = menu === "month" ? !showMonthDropdown.value : false;
  showDayDropdown.value = menu === "day" ? !showDayDropdown.value : false;
  showYearDropdown.value = menu === "year" ? !showYearDropdown.value : false;
}
</script>

<template>
  <Transition name="fade-blur">
    <div
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
    >
      <div
        class="bg-white rounded-[28px] p-10 max-w-[500px] w-full shadow-2xl relative"
      >
        <h2 class="text-2xl font-bold text-[#03335C] mb-2">
          {{ t("verifyIdentity") }}
        </h2>
        <p class="text-gray-500 text-sm mb-6">
          {{ t("enterBirthdateFor") }}
          <strong
            >{{ selectedResident?.first_name }}
            {{ selectedResident?.last_name }}</strong
          >
          {{ t("toProceed") }}.
        </p>

        <div class="flex gap-3 mb-4">
          <!-- Month -->
          <div class="flex-1 relative">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("month") }}</label
            >
            <button
              @click="toggle('month')"
              class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
            >
              {{
                months.find((m) => m.value === verifyMonth)?.name || t("select")
              }}
              <ChevronDownIcon class="w-4 h-4" />
            </button>
            <div
              v-if="showMonthDropdown"
              class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
            >
              <button
                v-for="m in months"
                :key="m.value"
                @click="
                  emit('update:verifyMonth', m.value);
                  showMonthDropdown = false;
                "
                class="w-full text-left py-2 px-3 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
              >
                {{ m.name }}
              </button>
            </div>
          </div>

          <!-- Day -->
          <div class="flex-1 relative">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("day") }}</label
            >
            <button
              @click="toggle('day')"
              class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
            >
              {{ verifyDay || t("dd") }}
              <ChevronDownIcon class="w-4 h-4" />
            </button>
            <div
              v-if="showDayDropdown"
              class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
            >
              <button
                v-for="d in days"
                :key="d"
                @click="
                  emit('update:verifyDay', d);
                  showDayDropdown = false;
                "
                class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
              >
                {{ d }}
              </button>
            </div>
          </div>

          <!-- Year -->
          <div class="flex-1 relative">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("year") }}</label
            >
            <button
              @click="toggle('year')"
              class="w-full h-11 border border-gray-300 rounded-xl px-3 flex items-center justify-between text-[#03335C] font-bold bg-white text-sm hover:border-[#03335C]"
            >
              {{ verifyYear || t("yyyy") }}
              <ChevronDownIcon class="w-4 h-4" />
            </button>
            <div
              v-if="showYearDropdown"
              class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-[60] p-1 flex flex-col h-40 overflow-y-auto custom-scroll"
            >
              <button
                v-for="y in years"
                :key="y"
                @click="
                  emit('update:verifyYear', y);
                  showYearDropdown = false;
                "
                class="w-full text-center py-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm"
              >
                {{ y }}
              </button>
            </div>
          </div>
        </div>

        <p
          v-if="verificationError"
          class="text-red-500 text-xs font-bold mb-4 animate-shake"
        >
          {{ verificationError }}
        </p>

        <div class="flex gap-4 mt-8">
          <Button
            variant="outline"
            class="flex-1"
            :disabled="isVerifying"
            @click="emit('close')"
            >{{ t("cancel") }}</Button
          >
          <Button
            :variant="isVerifying ? 'disabled' : 'secondary'"
            class="flex-1"
            :disabled="isVerifying"
            @click="emit('verify')"
          >
            {{ isVerifying ? t("verifying") : t("verifyAndProceed") }}
          </Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 6px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background-color: #bde0ef;
  border-radius: 20px;
}
.modal-backdrop {
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  backdrop-filter: blur(8px);
}
.animate-shake {
  animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}
@keyframes shake {
  10%,
  90% {
    transform: translate3d(-1px, 0, 0);
  }
  20%,
  80% {
    transform: translate3d(2px, 0, 0);
  }
  30%,
  50%,
  70% {
    transform: translate3d(-4px, 0, 0);
  }
  40%,
  60% {
    transform: translate3d(4px, 0, 0);
  }
}
</style>
