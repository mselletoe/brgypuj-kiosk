<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import {
  UserCircleIcon,
  QrCodeIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  IdentificationIcon,
  PlusIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();
const authStore = useAuthStore();

const isGuest = computed(() => authStore.isGuest);

// Both guest and logged-in users now use the Apply process
const handleApplyRFID = () => router.push("/id-services/apply");

const handleChangePasscode = () => router.push("/id-services/change-pin");
const handleReportLost = () => router.push("/id-services/report-lost");

const resident = computed(() => {
  const res = authStore.resident || {};
  return {
    firstName: res.first_name || "",
    middleName: res.middle_name || "",
    lastName: res.last_name || "",
    id: res.id || "N/A",
    rfid: authStore.rfidUid || "N/A",
    address: res.address || "No Address Available",
  };
});

const goBack = () => router.push("/home");
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <div class="flex items-center mb-4 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          RFID Services
        </h1>
        <p class="text-[#03335C] -mt-2">
          Get, manage, or replace your Barangay RFID Card.
        </p>
      </div>
    </div>

    <div class="flex flex-row items-stretch justify-center gap-6 px-0.5 pt-2 pb-8 flex-1">
      <div class="flex-1">
        <!-- Logged In User -->
        <div
          v-if="!isGuest"
          class="relative h-full bg-gradient-to-br from-[#003A6B] to-[#005B96] rounded-3xl shadow-[0_10px_30px_-5px_rgba(0,0,0,0.15)] overflow-hidden text-white p-8 flex flex-col justify-between transform transition-transform active:scale-[0.99] duration-300 border border-white/10"
        >
          <div
            class="absolute top-0 right-0 w-80 h-80 bg-white/5 rounded-full -mr-24 -mt-24 pointer-events-none"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-64 h-64 bg-white/5 rounded-full -ml-16 -mb-16 pointer-events-none"
          ></div>

          <div class="flex justify-between items-start z-10">
            <div class="flex gap-4 items-center">
              <img
                src="@/assets/images/Pob1Logo.svg"
                alt="Logo"
                class="w-14 h-14 bg-white rounded-full p-1 shadow-sm"
              />
              <div>
                <h3
                  class="font-bold text-xl leading-tight tracking-wide uppercase"
                >
                  Brgy. Poblacion 1
                </h3>
                <p class="text-[11px] opacity-70 uppercase tracking-widest">
                  Resident Identification
                </p>
              </div>
            </div>
            <div
              class="bg-[#21C05C]/20 backdrop-blur-md border border-[#21C05C] text-[#4ADE80] text-[11px] font-bold px-4 py-1.5 rounded-full flex items-center gap-2"
            >
              <span
                class="w-2 h-2 bg-[#4ADE80] rounded-full animate-pulse"
              ></span>
              ACTIVE
            </div>
          </div>

          <div class="flex gap-10 items-center z-10">
            <div
              class="w-32 h-32 bg-gray-200 rounded-xl flex items-center justify-center text-gray-400 shadow-inner border-2 border-white/20 flex-shrink-0"
            >
              <UserCircleIcon class="w-24 h-24 opacity-80" />
            </div>
            <div class="flex-1 overflow-hidden">
              <p class="text-[11px] opacity-60 uppercase tracking-wider mb-1">
                Full Name
              </p>
              <h2
                class="text-2xl font-bold mb-4 drop-shadow-sm tracking-tight leading-none"
              >
                {{ resident.firstName }} {{ resident.middleName }} {{ resident.lastName }}
              </h2>
              <div>
                <p class="text-[11px] opacity-60 uppercase mb-1">
                  Address
                </p>
                <p class="text-lg font-semibold leading-tight">
                  {{ resident.address }}
                </p>
              </div>
            </div>
          </div>

          <div
            class="flex justify-between items-end z-10 pt-5 border-t border-white/10"
          >
            <div>
              <p class="text-[11px] opacity-60 uppercase tracking-wider mb-1">
                RFID UID
              </p>
              <p
                class="font-mono text-xl tracking-[0.25em] opacity-90 font-medium"
              >
                {{ resident.rfid }}
              </p>
            </div>
            <QrCodeIcon class="w-12 h-12 opacity-80" />
          </div>
        </div>

        <!-- Guest -->
        <div
          v-else
          class="relative h-full bg-gradient-to-br from-[#003A6B] to-[#005B96] rounded-3xl shadow-[0_10px_30px_-5px_rgba(0,0,0,0.15)] overflow-hidden text-white p-8 flex flex-col justify-center items-center text-center border border-white/10"
        >
          <div
            class="absolute top-0 right-0 w-80 h-80 bg-white/5 rounded-full -mr-24 -mt-24 pointer-events-none"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-64 h-64 bg-white/5 rounded-full -ml-16 -mb-16 pointer-events-none"
          ></div>

          <div class="z-10 flex flex-col items-center">
            <div
              class="w-24 h-24 bg-white/10 rounded-full flex items-center justify-center mb-6 backdrop-blur-sm border border-white/20"
            >
              <IdentificationIcon class="w-12 h-12 text-white" />
            </div>
            <h2 class="text-4xl font-bold mb-3 tracking-tight">No Active ID</h2>
            <p class="text-lg text-blue-100 max-w-md leading-relaxed">
              You are currently in Guest Mode. Apply for a Barangay RFID Card to
              access kiosk services easily.
            </p>
            <div
              class="mt-8 flex gap-2 items-center bg-white/10 px-6 py-2 rounded-full border border-white/20"
            >
              <div
                class="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"
              ></div>
              <span class="text-sm font-bold tracking-widest uppercase"
                >Application Open</span
              >
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-4 w-[360px]">
        <button
          @click="handleApplyRFID"
          class="flex-1 flex items-center px-6 bg-white rounded-2xl shadow-sm border-2 border-gray-100 active:border-[#21C05C] active:bg-gray-50 transition-all group text-left"
        >
          <div
            class="w-10 h-10 bg-green-50 rounded-full flex-shrink-0 flex items-center justify-center mr-3 group-active:bg-[#21C05C] transition-colors"
          >
            <PlusIcon class="w-6 h-6 text-[#21C05C] group-active:text-white" />
          </div>
          <div class="flex-1">
            <h3 class="font-bold text-[#03335C] text-xl leading-tight">
              Apply for RFID
            </h3>
            <p class="text-gray-500 text-sm mt-0.5">
              {{
                isGuest
                  ? "New resident application"
                  : "Replace or request new card"
              }}
            </p>
          </div>
        </button>

        <button
          @click="!isGuest && handleChangePasscode()"
          :class="[
            'flex-1 flex items-center px-6 rounded-2xl shadow-sm border-2 transition-all group text-left',
            isGuest
              ? 'bg-gray-50 border-gray-100 opacity-60 cursor-not-allowed'
              : 'bg-white border-gray-100 active:border-[#003A6B] active:bg-gray-50',
          ]"
        >
          <div
            :class="[
              'w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center mr-3 transition-colors',
              isGuest ? 'bg-gray-200' : 'bg-blue-50 group-active:bg-[#003A6B]',
            ]"
          >
            <LockClosedIcon
              :class="[
                'w-6 h-6',
                isGuest
                  ? 'text-gray-400'
                  : 'text-[#003A6B] group-active:text-white',
              ]"
            />
          </div>
          <div class="flex-1">
            <h3
              :class="[
                'font-bold text-xl leading-tight',
                isGuest ? 'text-gray-400' : 'text-[#03335C]',
              ]"
            >
              Change Passcode
            </h3>
            <p class="text-gray-400 text-sm mt-0.5">Update security PIN</p>
          </div>
        </button>

        <button
          @click="handleReportLost"
          class="flex-1 flex items-center px-6 bg-white rounded-2xl shadow-sm border-2 border-gray-100 active:border-[#F16C14] active:bg-gray-50 transition-all group text-left"
        >
          <div
            class="w-10 h-10 bg-orange-50 rounded-full flex-shrink-0 flex items-center justify-center mr-3 group-active:bg-[#F16C14] transition-colors"
          >
            <ExclamationTriangleIcon
              class="w-6 h-6 text-[#F16C14] group-active:text-white"
            />
          </div>
          <div class="flex-1">
            <h3 class="font-bold text-[#03335C] text-xl leading-tight">
              Report Lost Card
            </h3>
            <p class="text-gray-500 text-sm mt-0.5">Block access immediately</p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
