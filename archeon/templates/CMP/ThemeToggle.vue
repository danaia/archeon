<!-- @archeon:file -->
<!-- @glyph CMP:ThemeToggle -->
<!-- @intent Dark/light mode toggle button with icon switching -->
<!-- @chain @v1 TSK:toggle_theme => CMP:ThemeToggle => STO:Theme => OUT:theme_changed -->

<script setup>
// @archeon:section imports
import { ref } from 'vue';
import { useThemeStore, THEMES } from '@/stores/themeStore';
// @archeon:endsection

// @archeon:section props_and_state
defineProps({
  showLabel: {
    type: Boolean,
    default: false,
  },
});

const themeStore = useThemeStore();
const isOpen = ref(false);

const options = [
  { value: THEMES.LIGHT, label: 'Light', icon: '☀️' },
  { value: THEMES.DARK, label: 'Dark', icon: '🌙' },
  { value: THEMES.SYSTEM, label: 'System', icon: '💻' },
];
// @archeon:endsection

// @archeon:section handlers
function handleSelect(value) {
  themeStore.setTheme(value);
  isOpen.value = false;
}
// @archeon:endsection
</script>

<!-- @archeon:section render -->
<template>
  <div class="flex items-center gap-2">
    <!-- Simple toggle button -->
    <button
      type="button"
      class="btn-ghost p-2 rounded-md"
      :aria-label="`Switch to ${themeStore.isDark ? 'light' : 'dark'} mode`"
      @click="themeStore.toggleTheme()"
    >
      <!-- Sun icon (shown in dark mode) -->
      <svg
        v-if="themeStore.isDark"
        class="h-5 w-5 text-yellow-400"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fill-rule="evenodd"
          d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
          clip-rule="evenodd"
        />
      </svg>
      <!-- Moon icon (shown in light mode) -->
      <svg
        v-else
        class="h-5 w-5 text-content-secondary"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
      </svg>
    </button>
    
    <span v-if="showLabel" class="text-sm text-content-secondary">
      {{ themeStore.isDark ? 'Dark' : 'Light' }}
    </span>
  </div>
</template>
<!-- @archeon:endsection -->