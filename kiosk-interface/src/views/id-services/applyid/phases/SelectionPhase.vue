<script setup>
import { watch } from "vue";
import { useI18n } from "vue-i18n";
import {
  CalendarDaysIcon,
  UserIcon,
  ChevronDownIcon,
} from "@heroicons/vue/24/outline";

const props = defineProps({
  lastNameLetter: String,
  firstNameLetter: String,
  selectedResident: Object,
  residentList: Array,
  isFetching: Boolean,
});

const emit = defineEmits([
  "update:lastNameLetter",
  "update:firstNameLetter",
  "update:selectedResident",
  "fetch-residents",
]);

const { t } = useI18n();

const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// Dropdown visibility (local only)
import { ref } from "vue";
const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);

function toggleDropdown(menu) {
  showLastNameDropdown.value =
    menu === "lastName" ? !showLastNameDropdown.value : false;
  showFirstNameDropdown.value =
    menu === "firstName" ? !showFirstNameDropdown.value : false;
  showResidentDropdown.value =
    menu === "resident" ? !showResidentDropdown.value : false;
}

function selectLastNameLetter(letter) {
  emit("update:lastNameLetter", letter);
  showLastNameDropdown.value = false;
  emit("update:selectedResident", null);
}

function selectFirstNameLetter(letter) {
  emit("update:firstNameLetter", letter);
  showFirstNameDropdown.value = false;
  emit("update:selectedResident", null);
}

function selectResident(resident) {
  emit("update:selectedResident", resident);
  showResidentDropdown.value = false;
}

watch(
  () => [props.lastNameLetter, props.firstNameLetter],
  ([last, first]) => {
    emit("fetch-residents", last, first);
  },
);
</script>

<template>
  <div class="flex w-full h-full items-center justify-start animate-fadeIn">
    <div class="w-full flex flex-col relative px-2">
      <h2 class="text-[25px] font-bold text-[#03335C] text-left">
        {{ t("residentSelection") }}
      </h2>
      <p class="text-gray-500 italic text-xs mb-6 text-left">
        {{ t("selectResidentToLink") }}
      </p>

      <div class="space-y-4 w-full">
        <div class="flex gap-10 w-full">
          <!-- Last Name Letter -->
          <div class="flex flex-1 items-center gap-3">
            <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
              <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
              <div class="flex flex-col leading-tight">
                <span class="text-[9px] uppercase font-bold text-gray-400">{{
                  t("firstLetterOf")
                }}</span>
                <span
                  class="text-[#03335C] font-black text-sm uppercase tracking-tight"
                  >{{ t("surname") }}</span
                >
              </div>
            </div>
            <div class="flex-1 relative">
              <button
                @click="toggleDropdown('lastName')"
                class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
              >
                {{ lastNameLetter || t("select") }}
                <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
              </button>
              <div
                v-if="showLastNameDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll"
              >
                <button
                  v-for="l in alphabet"
                  :key="l"
                  @click="selectLastNameLetter(l)"
                  class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                >
                  {{ l }}
                </button>
              </div>
            </div>
          </div>

          <!-- First Name Letter -->
          <div class="flex flex-1 items-center gap-3">
            <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
              <CalendarDaysIcon class="w-5 h-5 text-[#03335C]" />
              <div class="flex flex-col leading-tight">
                <span class="text-[9px] uppercase font-bold text-gray-400">{{
                  t("firstLetterOf")
                }}</span>
                <span
                  class="text-[#03335C] font-black text-sm uppercase tracking-tight"
                  >{{ t("firstName") }}</span
                >
              </div>
            </div>
            <div class="flex-1 relative">
              <button
                @click="toggleDropdown('firstName')"
                class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
              >
                {{ firstNameLetter || t("select") }}
                <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
              </button>
              <div
                v-if="showFirstNameDropdown"
                class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 flex flex-col h-48 overflow-y-auto custom-scroll"
              >
                <button
                  v-for="l in alphabet"
                  :key="l"
                  @click="selectFirstNameLetter(l)"
                  class="w-full text-center py-2.5 px-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                >
                  {{ l }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Resident Name Dropdown -->
        <div class="flex items-center gap-3 w-full">
          <div class="flex items-center gap-2 flex-shrink-0 min-w-[140px]">
            <UserIcon class="w-5 h-5 text-[#03335C]" />
            <span
              class="text-[#03335C] font-bold text-[11px] uppercase tracking-tight"
              >{{ t("residentName") }}</span
            >
          </div>
          <div class="flex-1 relative">
            <button
              @click="toggleDropdown('resident')"
              :disabled="!lastNameLetter || !firstNameLetter || isFetching"
              class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors disabled:opacity-50 disabled:bg-gray-50"
            >
              <span v-if="isFetching" class="text-gray-400 text-sm italic">{{
                t("loading")
              }}</span>
              <span
                v-else-if="selectedResident"
                class="truncate text-[#03335C]"
              >
                {{ selectedResident.last_name }},
                {{ selectedResident.first_name }}
                <span v-if="selectedResident.middle_name">{{
                  selectedResident.middle_name
                }}</span>
              </span>
              <span v-else class="text-gray-400 truncate opacity-60">
                {{
                  !lastNameLetter || !firstNameLetter
                    ? t("selectInitialsFirst")
                    : t("selectResident")
                }}
              </span>
              <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
            </button>
            <div
              v-if="showResidentDropdown"
              class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-[150px] overflow-y-auto custom-scroll"
            >
              <div
                v-if="residentList.length === 0"
                class="p-3 text-center text-gray-400 text-sm"
              >
                {{ t("noRecordsFound") }}
              </div>
              <button
                v-for="r in residentList"
                :key="r.resident_id"
                @click="selectResident(r)"
                class="w-full text-left py-2 px-4 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-base border-b border-gray-50 last:border-0"
              >
                {{ r.last_name }}, {{ r.first_name }}
                <span v-if="r.middle_name">{{ r.middle_name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
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
.animate-fadeIn {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
