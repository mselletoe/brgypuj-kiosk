<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  ClockIcon,
  ArrowRightIcon,
} from "@heroicons/vue/24/solid";
import { useGlobalSearch } from "./useGlobalSearch";

const props = defineProps({
  modelValue: Boolean,
});
const emit = defineEmits(["update:modelValue"]);

const {
  query,
  results,
  hasResults,
  totalCount,
  isLoading,
  recentSearches,
  addToRecent,
  clearRecent,
  onKeydown,
} = useGlobalSearch();

const router = useRouter();
const inputRef = ref(null);

watch(
  () => props.modelValue,
  async (val) => {
    if (val) {
      await nextTick();
      inputRef.value?.focus();
    } else {
      query.value = "";
    }
  },
);

function handleClose() {
  emit("update:modelValue", false);
}

function navigate(item) {
  addToRecent(item.label);
  handleClose();
  router.push(item.route);
}

function searchRecent(term) {
  query.value = term;
  nextTick(() => inputRef.value?.focus());
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[9999] flex items-start justify-center pt-[12vh] px-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"
          @click="handleClose"
        />

        <!-- Panel -->
        <div
          class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-100"
        >
          <!-- Search input -->
          <div
            class="flex items-center gap-3 px-5 py-4 border-b border-gray-100"
          >
            <MagnifyingGlassIcon class="h-5 w-5 text-blue-500 shrink-0" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Search residents, documents, equipment, blotter…"
              class="flex-1 bg-transparent border-none outline-none text-sm text-gray-800 font-semibold placeholder:font-normal placeholder:text-gray-400"
            />
            <div class="flex items-center gap-2">
              <svg
                v-if="isLoading"
                class="animate-spin h-4 w-4 text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8z"
                />
              </svg>
              <span
                v-if="query && !isLoading"
                class="text-xs text-gray-400 font-medium"
              >
                {{ totalCount }} result{{ totalCount !== 1 ? "s" : "" }}
              </span>
              <button
                v-if="query"
                @click="
                  query = '';
                  inputRef.focus();
                "
                class="p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <XMarkIcon class="h-4 w-4 text-gray-400" />
              </button>
              <kbd
                class="hidden sm:inline-flex items-center px-2 py-0.5 text-[11px] font-medium text-gray-400 bg-gray-100 rounded-md border border-gray-200"
              >
                Esc
              </kbd>
            </div>
          </div>

          <!-- Body -->
          <div class="max-h-[55vh] overflow-y-auto">
            <!-- No query: show recents -->
            <template v-if="!query">
              <div v-if="recentSearches.length" class="p-4">
                <div class="flex justify-between items-center mb-2 px-1">
                  <span
                    class="text-xs font-bold text-gray-400 uppercase tracking-wider"
                    >Recent</span
                  >
                  <button
                    @click="clearRecent"
                    class="text-xs text-gray-400 hover:text-red-400 transition-colors"
                  >
                    Clear
                  </button>
                </div>
                <button
                  v-for="term in recentSearches"
                  :key="term"
                  @click="searchRecent(term)"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 transition-colors text-left"
                >
                  <ClockIcon class="h-4 w-4 text-gray-300 shrink-0" />
                  <span class="text-sm text-gray-600 font-medium">{{
                    term
                  }}</span>
                </button>
              </div>
              <div v-else class="py-16 text-center text-sm text-gray-400">
                Start typing to search everything…
              </div>
            </template>

            <!-- Loading -->
            <div
              v-else-if="isLoading"
              class="py-16 text-center text-sm text-gray-400"
            >
              Searching…
            </div>

            <!-- No results -->
            <div v-else-if="!hasResults" class="py-16 text-center">
              <p class="text-sm font-semibold text-gray-500">
                No results for "<span class="text-gray-800">{{ query }}</span
                >"
              </p>
              <p class="text-xs text-gray-400 mt-1">
                Try a name, ID, transaction number, or status
              </p>
            </div>

            <!-- Grouped results -->
            <div v-else>
              <div
                v-for="group in results"
                :key="group.type"
                class="border-b border-gray-50 last:border-b-0"
              >
                <div class="px-5 pt-3 pb-1 flex items-center gap-2">
                  <span class="text-base">{{ group.icon }}</span>
                  <span
                    class="text-xs font-bold text-gray-400 uppercase tracking-wider"
                  >
                    {{ group.label }}
                  </span>
                </div>
                <button
                  v-for="item in group.items"
                  :key="item.id"
                  @click="navigate(item)"
                  class="w-full flex items-center justify-between px-5 py-3 hover:bg-blue-50 transition-colors group text-left"
                >
                  <div>
                    <p
                      class="text-sm font-bold text-gray-800 group-hover:text-blue-700 transition-colors"
                    >
                      {{ item.label }}
                    </p>
                    <p class="text-xs text-gray-400 mt-0.5">
                      {{ item.subtitle }}
                    </p>
                  </div>
                  <ArrowRightIcon
                    class="h-4 w-4 text-gray-300 group-hover:text-blue-400 transition-colors shrink-0"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div
            class="px-5 py-2.5 border-t border-gray-50 flex items-center gap-4 bg-gray-50/50"
          >
            <span class="text-[11px] text-gray-400"
              ><kbd class="font-semibold">↵</kbd> open</span
            >
            <span class="text-[11px] text-gray-400"
              ><kbd class="font-semibold">Esc</kbd> close</span
            >
            <span class="text-[11px] text-gray-400"
              ><kbd class="font-semibold">Ctrl K</kbd> toggle</span
            >
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
