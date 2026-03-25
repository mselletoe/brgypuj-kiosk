<script setup>
import { useI18n } from "vue-i18n";
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
          <!-- Month — native select for smooth performance on Pi -->
          <div class="flex-1 flex flex-col">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("month") }}</label
            >
            <select
              :value="verifyMonth"
              @change="emit('update:verifyMonth', $event.target.value)"
              class="native-select"
            >
              <option value="" disabled>{{ t("select") }}</option>
              <option v-for="m in months" :key="m.value" :value="m.value">
                {{ m.name }}
              </option>
            </select>
          </div>

          <!-- Day -->
          <div class="flex-1 flex flex-col">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("day") }}</label
            >
            <select
              :value="verifyDay"
              @change="emit('update:verifyDay', $event.target.value)"
              class="native-select"
            >
              <option value="" disabled>{{ t("dd") }}</option>
              <option v-for="d in days" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <!-- Year -->
          <div class="flex-1 flex flex-col">
            <label
              class="block text-[10px] font-bold text-gray-400 uppercase mb-1"
              >{{ t("year") }}</label
            >
            <select
              :value="verifyYear"
              @change="emit('update:verifyYear', $event.target.value)"
              class="native-select"
            >
              <option value="" disabled>{{ t("yyyy") }}</option>
              <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
            </select>
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
          >
            {{ t("cancel") }}
          </Button>
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
.native-select {
  height: 44px;
  width: 100%;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  background-color: #ffffff;
  color: #03335c;
  font-weight: 700;
  font-size: 0.875rem;
  appearance: auto;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
}
.native-select:focus {
  border-color: #03335c;
}
.native-select:hover {
  border-color: #03335c;
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
