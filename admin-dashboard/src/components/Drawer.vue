<script setup>
import { useRoute, useRouter } from "vue-router";
import { NButton } from "naive-ui";
import { ref, watch, nextTick, onMounted } from "vue";
import {
  HomeIcon,
  DocumentTextIcon,
  WrenchScrewdriverIcon,
  ChatBubbleLeftRightIcon,
  SpeakerWaveIcon,
  FolderOpenIcon,
  CircleStackIcon,
  QuestionMarkCircleIcon,
  UserGroupIcon,
  UserCircleIcon,
} from "@heroicons/vue/24/solid";

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const router = useRouter();
const route = useRoute();

const menuGroups = [
  {
    title: null,
    items: [
      { label: "Overview", icon: HomeIcon, to: "/overview" },
      {
        label: "Document Requests",
        icon: DocumentTextIcon,
        to: "/document-requests",
      },
      {
        label: "Equipment Requests",
        icon: WrenchScrewdriverIcon,
        to: "/equipment-requests",
      },
      {
        label: "Feedback and Reports",
        icon: ChatBubbleLeftRightIcon,
        to: "/feedback-and-reports",
      },
    ],
  },
  {
    title: "SYSTEM MANAGERS",
    items: [
      {
        label: "Document Services",
        icon: FolderOpenIcon,
        to: "/document-services",
      },
      {
        label: "Equipment Inventory",
        icon: CircleStackIcon,
        to: "/equipment-inventory",
      },
      {
        label: "Kiosk Announcements",
        icon: SpeakerWaveIcon,
        to: "/kiosk-announcements",
      },
      {
        label: "Blotter and KP Logs",
        icon: UserCircleIcon,
        to: "/blotter-kp-logs",
      },
      {
        label: "Residents Information",
        icon: UserGroupIcon,
        to: "/residents-management",
      },
    ],
  },
  {
    title: "HELP & SUPPORT",
    items: [
      {
        label: "FAQs Management",
        icon: QuestionMarkCircleIcon,
        to: "/faqs-management",
      },
      {
        label: "Contact Information",
        icon: UserCircleIcon,
        to: "/contact-information",
      },
    ],
  },
];

const isActive = (path) => route.path.startsWith(path);

// --- Sliding marker logic ---
const navContainerRef = ref(null);
const buttonRefs = ref({});
const markerTop = ref(0);
const markerVisible = ref(false);

const updateMarker = async () => {
  await nextTick();
  if (!navContainerRef.value) return;

  const activePath = menuGroups
    .flatMap((g) => g.items)
    .map((i) => i.to)
    .find((to) => route.path.startsWith(to));

  // Fix: If there is no active path (e.g., we are on Settings), hide the marker!
  if (!activePath || !buttonRefs.value[activePath]) {
    markerVisible.value = false;
    return;
  }

  const btnEl =
    buttonRefs.value[activePath].$el ?? buttonRefs.value[activePath];
  const containerRect = navContainerRef.value.getBoundingClientRect();
  const btnRect = btnEl.getBoundingClientRect();

  markerTop.value = btnRect.top - containerRect.top;
  markerVisible.value = true;
};

watch(() => route.path, updateMarker);
watch(() => props.isOpen, updateMarker);
onMounted(updateMarker);
</script>

<template>
  <div class="w-full h-full select-none mt-2">
    <nav class="space-y-6 overflow-visible">
      <!-- Wrap everything in a relative container so the marker can position against it -->
      <div ref="navContainerRef" class="relative">
        <!-- The sliding pill marker -->
        <div
          v-if="markerVisible"
          class="sliding-marker"
          :class="isOpen ? 'sliding-marker--open' : 'sliding-marker--closed'"
          :style="{ top: markerTop + 'px' }"
        />

        <div
          v-for="(group, index) in menuGroups"
          :key="index"
          class="overflow-visible"
          :class="index > 0 ? 'mt-6' : ''"
        >
          <h3
            v-if="group.title"
            class="px-3 text-[10px] font-black text-gray-400 tracking-widest mb-2 transition-opacity duration-200 whitespace-nowrap"
            :class="isOpen ? 'opacity-100' : 'opacity-0'"
          >
            {{ group.title }}
          </h3>

          <ul class="space-y-1.5 overflow-visible">
            <li
              v-for="item in group.items"
              :key="item.to"
              class="relative flex justify-start overflow-visible"
            >
              <n-button
                :ref="
                  (el) => {
                    if (el) buttonRefs[item.to] = el;
                  }
                "
                quaternary
                class="nav-btn relative z-10 border-none"
                :class="[
                  isActive(item.to)
                    ? 'active-nav'
                    : 'inactive-nav hover:bg-gray-50',
                  isOpen ? 'open-mode' : 'closed-mode',
                ]"
                @click="router.push(item.to)"
              >
                <div class="nav-inner">
                  <component
                    :is="item.icon"
                    class="w-[24px] h-[24px] shrink-0 nav-icon"
                  />
                  <span
                    class="nav-text font-bold text-[13.5px] whitespace-nowrap"
                    :class="isOpen ? 'nav-text--visible' : 'nav-text--hidden'"
                  >
                    {{ item.label }}
                  </span>
                </div>
              </n-button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<style scoped>
/* ==================================
   BASE NAV STYLES
   ================================== */
.nav-btn {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  overflow: hidden !important;
}
.nav-btn :deep(.n-button__content) {
  width: 100%;
  display: flex;
  overflow: hidden;
}

.nav-inner {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  padding-left: 14px;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-text {
  margin-left: 12px;
}

.nav-text--visible {
  opacity: 1;
  pointer-events: auto;
  transition: opacity 0.15s ease;
}

.nav-text--hidden {
  opacity: 0;
  pointer-events: none;
  transition: none;
}

/* ==================================
   SLIDING MARKER
   ================================== */
.sliding-marker {
  position: absolute;
  left: 0;
  height: 52px;
  border-radius: 16px;
  pointer-events: none;
  z-index: 0;
  transition:
    top 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Open: subtle blue tint bg (text color is handled separately) */
.sliding-marker--open {
  width: 100%;
  background-color: transparent;
}

/* Closed: solid blue square with glow + liquid wave */
.sliding-marker--closed {
  width: 52px;
  background-color: #0957ff;
  box-shadow: 0 6px 16px -4px rgba(9, 87, 255, 0.3);
  animation: liquid-wave 2s ease-in-out infinite alternate;
}

/* ==================================
   OPEN STATE (MAXIMIZED)
   ================================== */
.open-mode {
  width: 100% !important;
  height: 52px !important;
  border-radius: 16px !important;
  padding: 0 !important;
  position: relative;
  z-index: 1;
}
.inactive-nav.open-mode {
  color: #64748b !important;
}
/* Active button is transparent — marker provides the bg */
.active-nav.open-mode {
  background-color: transparent !important;
  color: #0957ff !important;
}

/* ==================================
   CLOSED STATE (MINIMIZED)
   ================================== */
.closed-mode {
  width: 52px !important;
  height: 52px !important;
  border-radius: 16px !important;
  padding: 0 !important;
  background-color: transparent !important;
  position: relative;
  z-index: 1;
}

/* Active button is transparent — marker provides the bg */
.active-nav.closed-mode {
  background-color: transparent !important;
  color: white !important;
  box-shadow: none !important;
  animation: none !important;
}
.active-nav.closed-mode .nav-icon {
  color: white !important;
}

/* Floating tooltip shown on hover in closed mode */
.closed-mode .nav-text--hidden {
  position: absolute;
  left: 68px;
  margin-left: 0;
  background-color: white;
  color: #0957ff !important;
  padding: 8px 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
  opacity: 0;
  transform: translateX(-5px);
  transition: none;
  pointer-events: none;
}
.closed-mode:hover .nav-text--hidden {
  opacity: 1;
  transform: translateX(0);
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.inactive-nav.closed-mode {
  color: #64748b !important;
}

/* ==================================
   CLOSED HOVER STATE
   ================================== */
.inactive-nav.closed-mode:hover {
  background-color: #f8fafc !important;
  color: #0957ff !important;
}

/* Liquid Wave */
@keyframes liquid-wave {
  0% {
    border-radius: 16px 22px 18px 24px / 20px 16px 24px 18px;
  }
  50% {
    border-radius: 20px 18px 24px 18px / 18px 22px 16px 24px;
  }
  100% {
    border-radius: 18px 24px 16px 22px / 22px 18px 24px 16px;
  }
}
</style>
