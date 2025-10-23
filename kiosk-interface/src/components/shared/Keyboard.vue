<script setup>
import { ref, computed, watch } from 'vue';
import {
  ArrowUturnLeftIcon as ArrowUturnLeftIconOutline,
  BackspaceIcon as BackspaceIconOutline,
  ArrowUpIcon as ArrowUpIconOutline,
  SquaresPlusIcon as SquaresPlusIconOutline
} from '@heroicons/vue/24/outline';
import {
  ArrowUturnLeftIcon as ArrowUturnLeftIconSolid,
  ArrowUpIcon as ArrowUpIconSolid,
} from '@heroicons/vue/24/solid';

const emit = defineEmits(['key-press', 'delete', 'enter', 'tab', 'layout-change', 'hide-keyboard']);

const alphaLayout = [
  ['tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'backspace'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'enter'],
  ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', 'shift'],
  ['.?123', 'space', '.?123', 'hide'],
];

const shiftedAlphaLayout = [
  ['tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'backspace'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'enter'],
  ['shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', 'shift'],
  ['.?123', 'space', '.?123', 'hide'],
];

const numericLayout = [
  ['tab', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'backspace'],
  ['return', '@', '#', 'P', '&', '*', '(', ')', "'", '"', 'enter'],
  ['#+=', '%', '-', '+', '=', '/', ';', ':', ',', '.', '#+='],
  ['ABC', 'space', 'ABC', 'hide'],
];

const symbolsLayout = [
  ['tab', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'backspace'],
  ['return', '$', '¥', '€', '-', '^', '[', ']', '{', '}', 'enter'],
  ['#+=', '§', '|', '~', '...', '\\', '<', '>', '!', '?', '#+='],
  ['ABC', 'space', 'ABC', 'hide'],
];


const currentLayout = ref('alpha');
const shiftActive = ref(false);
const capsLockActive = ref(false);

const activeLayout = computed(() => {
  if (currentLayout.value === 'alpha') {
    return shiftActive.value ? shiftedAlphaLayout : alphaLayout;
  } else if (currentLayout.value === 'numeric') {
    return numericLayout;
  } else if (currentLayout.value === 'symbols') {
    return symbolsLayout;
  }
  return alphaLayout;
});

const isAlphaLayout = computed(() => currentLayout.value === 'alpha');

const handleKeyPress = (key) => {
  switch (key) {
    case 'backspace': emit('delete'); break;
    case 'enter': emit('enter'); break;
    case 'return': emit('enter'); break;
    case 'tab': emit('tab'); break;
    case 'space': emit('key-press', ' '); break;
    case 'shift':
      if (isAlphaLayout.value) {
        shiftActive.value = !shiftActive.value;
      }
      break;
    case '.?123': currentLayout.value = 'numeric'; break;
    case '#+=': currentLayout.value = 'symbols'; break;
    case 'ABC': currentLayout.value = 'alpha'; break;
    case 'hide': emit('hide-keyboard'); break;
    case '...': emit('key-press', '...'); break;
    default:
      emit('key-press', key);
      if (shiftActive.value && isAlphaLayout.value && !capsLockActive.value) {
        shiftActive.value = false;
      }
      break;
  }
};

watch(currentLayout, () => {
  shiftActive.value = false;
  capsLockActive.value = false;
});

const getKeyStyle = (key) => {
  const functionKeys = ['tab', 'shift', 'backspace', 'enter', 'return', '.?123', '#+=', 'ABC', 'hide'];
  if (functionKeys.includes(key)) {
    if (key === 'shift' && shiftActive.value && isAlphaLayout.value) {
       return 'bg-white text-[#013C6D]';
    }
    return 'bg-gray-300 hover:bg-gray-400';
  }
  return 'bg-white hover:bg-gray-100';
};

const getKeyWidth = (key, rowIndex) => {
    if (rowIndex === 0) {
        if (key === 'tab') return 'w-[50px]';
        if (key === 'backspace') return 'w-[70px]';
        return 'flex-1';
    }
    if (rowIndex === 1 && currentLayout.value === 'alpha') {
         if (key === 'enter') return 'w-[80px]';
         return 'flex-1';
    }
    if (rowIndex === 1 && (currentLayout.value === 'numeric' || currentLayout.value === 'symbols')) {
        if (key === 'return') return 'w-[70px]';
        if (key === 'enter') return 'w-[70px]';
        return 'flex-1';
    }
    if (rowIndex === 2) {
        if (key === 'shift' && currentLayout.value === 'alpha') return 'w-[90px]';
        if ((key === '#+=' && currentLayout.value === 'numeric') || (key === '#+=' && currentLayout.value === 'symbols')) return 'w-[70px]';
        if (key === 'ABC' && currentLayout.value === 'symbols') return 'w-[70px]'
        return 'flex-1';
    }
    if (rowIndex === 3) {
        if (key === 'space') return 'flex-grow';
        if (key === '.?123' || key === 'ABC') return 'w-[90px]';
        if (key === 'hide') return 'w-[70px]';
    }
    return 'flex-1';
}

</script>

<template>
  <div class="fixed bottom-0 left-0 right-0 bg-gray-100 p-2 shadow-2xl z-50 rounded-t-xl">
    <div class="max-w-screen-lg mx-auto space-y-2">
      <div
        v-for="(row, rowIndex) in activeLayout"
        :key="rowIndex"
        :class="['flex gap-1.5']"
        :style="{ paddingLeft: rowIndex === 1 && isAlphaLayout ? '30px' : '0px', paddingRight: rowIndex === 1 && isAlphaLayout ? '30px' : '0px' }"
      >
        <button
          v-for="(key, keyIndex) in row"
          :key="`${rowIndex}-${keyIndex}`"
          @click="handleKeyPress(key)"
          :class="[
            'flex items-center justify-center rounded-md h-12 text-lg font-medium text-gray-800 transition-colors',
            'active:bg-gray-400 select-none',
            getKeyStyle(key),
            getKeyWidth(key, rowIndex)
          ]"
        >
          <BackspaceIconOutline v-if="key === 'backspace'" class="w-5 h-5" />
          <ArrowUpIconSolid v-else-if="key === 'shift' && shiftActive && isAlphaLayout" class="w-5 h-5" />
          <ArrowUpIconOutline v-else-if="key === 'shift' && !shiftActive && isAlphaLayout" class="w-5 h-5 transform rotate-180" />
          <ArrowUturnLeftIconSolid v-else-if="key === 'enter'" class="w-5 h-5" />
          <ArrowUturnLeftIconOutline v-else-if="key === 'return'" class="w-5 h-5" />
          <span v-else-if="key === 'space'" class="text-sm">space</span>
          <span v-else-if="key === 'tab'" class="text-sm">tab</span>
          <SquaresPlusIconOutline v-else-if="key === 'hide'" class="w-5 h-5" />
          <span v-else>{{ key }}</span>
        </button>
      </div>
    </div>
  </div>
</template>