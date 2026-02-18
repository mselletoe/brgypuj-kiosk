<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Modal from "@/components/shared/Modal.vue";
import {
  CalendarDaysIcon,
  UserIcon,
  ChevronDownIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();

// State
const lastNameLetter = ref("");
const firstNameLetter = ref("");
const selectedResident = ref(null);
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const referenceId = ref("");

// Dropdown Visibility State
const showLastNameDropdown = ref(false);
const showFirstNameDropdown = ref(false);
const showResidentDropdown = ref(false);

const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// Mock Database
const mockResidents = [
  {
    id: 1,
    firstName: "Aaron",
    lastName: "Abad",
    address: "Block 5 Lot 2",
    birthdate: "1998-05-12",
    rfid: "N/A",
  },
  {
    id: 2,
    firstName: "Adrian",
    lastName: "Agoncillo",
    address: "Block 12 Lot 1",
    birthdate: "2001-11-03",
    rfid: "N/A",
  },
  {
    id: 3,
    firstName: "Bea",
    lastName: "Alonzo",
    address: "Block 3 Lot 8",
    birthdate: "1995-02-14",
    rfid: "N/A",
  },
  {
    id: 7,
    firstName: "Keanno",
    lastName: "Macatangay",
    address: "Makati Homes 2",
    birthdate: "2003-01-15",
    rfid: "N/A",
  },
];

// Computed Filter
const filteredResidents = computed(() => {
  if (!lastNameLetter.value) return [];
  return mockResidents.filter((r) =>
    r.lastName.startsWith(lastNameLetter.value),
  );
});

// Actions
const goBack = () => router.push("/id-services");

const selectLastNameLetter = (letter) => {
  lastNameLetter.value = letter;
  showLastNameDropdown.value = false;
  selectedResident.value = null;
};

const selectFirstNameLetter = (letter) => {
  firstNameLetter.value = letter;
  showFirstNameDropdown.value = false;
};

const selectResident = (resident) => {
  selectedResident.value = resident;
  showResidentDropdown.value = false;
};

const handleReset = () => {
  lastNameLetter.value = "";
  firstNameLetter.value = "";
  selectedResident.value = null;
};

const handleSubmit = () => {
  if (!selectedResident.value) return;
  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    referenceId.value = `APP-${Math.floor(100000 + Math.random() * 900000)}`;
    showSuccessModal.value = true;
  }, 1500);
};

const handleModalDone = () => router.push("/id-services");
</script>

<template>
  <div
    class="flex flex-col w-full h-full bg-white overflow-hidden select-none no-scrollbar"
  >
    <div v-if="!showSuccessModal" class="flex flex-col h-full pt-4">
      <div class="flex items-center mb-1 gap-6 flex-shrink-0 px-8">
        <ArrowBackButton @click="goBack" />
        <div>
          <h1 class="text-[32px] text-[#03335C] font-bold tracking-tight">
            RFID Services
          </h1>
          <p class="text-[#03335C] text-sm opacity-80 -mt-1">
            Get, manage, or replace your RFID Card.
          </p>
        </div>
      </div>

      <div class="flex-1 px-4 flex items-center justify-center">
        <div
          class="w-full max-w-[1050px] h-[455px] bg-white rounded-[28px] shadow-[0_4px_20px_rgba(0,0,0,0.1)] border border-gray-100 flex p-8 gap-10 relative"
        >
          <div class="flex-1 flex flex-col relative">
            <h2 class="text-2xl font-bold text-[#03335C] mb-1">
              Apply for RFID Card
            </h2>
            <p class="text-gray-500 italic text-xs mb-6">
              Select the Resident to be linked to the new RFID card
            </p>

            <div class="space-y-3 flex-1 z-20">
              <div class="flex items-center justify-between relative">
                <div class="flex items-center gap-3">
                  <CalendarDaysIcon class="w-6 h-6 text-[#03335C]" />
                  <span class="text-[#03335C] font-medium text-sm">
                    Select first letter of
                    <span class="font-bold">LAST NAME</span>
                  </span>
                </div>

                <div class="relative">
                  <button
                    @click="showLastNameDropdown = !showLastNameDropdown"
                    class="w-32 h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                  >
                    {{ lastNameLetter || "" }}
                    <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                  </button>

                  <div
                    v-if="showLastNameDropdown"
                    class="absolute top-full right-0 w-32 mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 h-48 overflow-y-auto custom-scroll"
                  >
                    <button
                      v-for="l in alphabet"
                      :key="l"
                      @click="selectLastNameLetter(l)"
                      class="w-full text-center p-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                    >
                      {{ l }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between relative">
                <div class="flex items-center gap-3">
                  <CalendarDaysIcon class="w-6 h-6 text-[#03335C]" />
                  <span class="text-[#03335C] font-medium text-sm">
                    Select first letter of
                    <span class="font-bold">FIRST NAME</span>
                  </span>
                </div>

                <div class="relative">
                  <button
                    @click="showFirstNameDropdown = !showFirstNameDropdown"
                    class="w-32 h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                  >
                    {{ firstNameLetter || "" }}
                    <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                  </button>

                  <div
                    v-if="showFirstNameDropdown"
                    class="absolute top-full right-0 w-32 mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 h-48 overflow-y-auto custom-scroll"
                  >
                    <button
                      v-for="l in alphabet"
                      :key="l"
                      @click="selectFirstNameLetter(l)"
                      class="w-full text-center p-2 hover:bg-blue-50 rounded-lg font-bold text-[#03335C]"
                    >
                      {{ l }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="relative pt-2">
                <div class="flex items-center gap-2 mb-2">
                  <UserIcon class="w-5 h-5 text-[#03335C]" />
                  <span class="text-[#03335C] font-bold text-sm"
                    >Select Resident</span
                  >
                </div>
                <button
                  @click="showResidentDropdown = !showResidentDropdown"
                  class="w-full h-11 border border-gray-300 rounded-xl px-4 flex items-center justify-between text-[#03335C] font-bold bg-white text-base hover:border-[#03335C] transition-colors"
                  :disabled="!lastNameLetter"
                >
                  <span v-if="selectedResident" class="truncate"
                    >{{ selectedResident.lastName }},
                    {{ selectedResident.firstName }}</span
                  >
                  <span v-else class="text-gray-400 truncate opacity-60">
                    {{ lastNameLetter ? "Select Name..." : "" }}
                  </span>
                  <ChevronDownIcon class="w-5 h-5 text-[#03335C]" />
                </button>

                <div
                  v-if="showResidentDropdown && lastNameLetter"
                  class="absolute top-full left-0 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-1 max-h-40 overflow-y-auto custom-scroll"
                >
                  <div
                    v-if="filteredResidents.length === 0"
                    class="p-3 text-center text-gray-400 text-sm"
                  >
                    No records found
                  </div>
                  <button
                    v-for="r in filteredResidents"
                    :key="r.id"
                    @click="selectResident(r)"
                    class="w-full text-left p-3 hover:bg-blue-50 rounded-lg font-bold text-[#03335C] text-sm border-b border-gray-50 last:border-0"
                  >
                    {{ r.lastName }}, {{ r.firstName }}
                  </button>
                </div>
              </div>
            </div>

            <button
              @click="goBack"
              class="mt-auto w-32 py-2.5 border-2 border-[#03335C] text-[#03335C] rounded-xl font-bold hover:bg-blue-50 transition-colors text-base"
            >
              Cancel
            </button>
          </div>

          <div class="w-[340px] flex flex-col gap-3">
            <div
              class="bg-[#EAF6FB] rounded-xl p-5 border border-[#BDE0EF] h-[220px] flex flex-col justify-center"
            >
              <h3 class="text-xl font-bold text-[#03335C] text-center mb-0.5">
                Resident Details
              </h3>
              <p
                class="text-center text-[#03335C] text-[10px] italic opacity-70 mb-4"
              >
                Check details before submitting
              </p>

              <div class="space-y-1.5 text-[#03335C]">
                <div class="flex">
                  <span class="w-24 font-bold text-xs">RFID No.:</span>
                  <span class="font-medium text-xs">{{
                    selectedResident?.rfid || "---"
                  }}</span>
                </div>
                <div class="flex">
                  <span class="w-24 font-bold text-xs">Name:</span>
                  <span class="font-medium text-xs truncate">{{
                    selectedResident
                      ? `${selectedResident.firstName} ${selectedResident.lastName}`
                      : "---"
                  }}</span>
                </div>
                <div class="flex">
                  <span class="w-24 font-bold text-xs">Address:</span>
                  <span class="font-medium text-xs truncate">{{
                    selectedResident?.address || "---"
                  }}</span>
                </div>
                <div class="flex">
                  <span class="w-24 font-bold text-xs">Birthdate:</span>
                  <span class="font-medium text-xs">{{
                    selectedResident?.birthdate || "---"
                  }}</span>
                </div>
              </div>
            </div>

            <div class="flex flex-col gap-3 mt-auto">
              <button
                @click="handleReset"
                class="w-full py-3 bg-[#C8D1D8] text-white font-bold text-lg rounded-xl shadow-sm hover:bg-gray-400 transition-colors"
              >
                Reset
              </button>

              <button
                @click="handleSubmit"
                :disabled="!selectedResident || isSubmitting"
                :class="[
                  'w-full py-3 font-bold text-lg rounded-xl shadow-sm transition-colors',
                  !selectedResident || isSubmitting
                    ? 'bg-[#C8D1D8] text-white cursor-not-allowed'
                    : 'bg-[#B0C4D1] text-white hover:bg-[#90AAB9]',
                ]"
              >
                {{ isSubmitting ? "Processing..." : "Submit" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Modal
      v-else
      title="Application Received!"
      message="Your application has been logged. Please proceed to Window 2 and present your Reference ID to claim your card."
      :reference-id="referenceId"
      :show-reference-id="true"
      primary-button-text="Done"
      @primary-click="handleModalDone"
    />
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Custom Scrollbar for Dropdowns */
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
</style>
