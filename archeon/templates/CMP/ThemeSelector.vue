<!-- @archeon:file -->
<!-- @glyph CMP:ThemeSelector -->
<!-- @intent Dropdown selector for light/dark/system theme -->
<!-- @chain @v1 TSK:select_theme => CMP:ThemeSelector => STO:Theme => OUT:theme_changed -->

<script setup>
// @archeon:section imports
import { ref, onMounted, onUnmounted } from 'vue';
import { useThemeStore, THEMES } from '@/stores/themeStore';
// @archeon:endsection

// @archeon:section props_and_state
const themeStore = useThemeStore();
const isOpen = ref(false);
const dropdownRef = ref(null);

const options = [
  { value: THEMES.LIGHT, label: 'Light', icon: '☀️' },
  { value: THEMES.DARK, label: 'Dark', icon: '🌙' },
  { value: THEMES.SYSTEM, label: 'System', icon: '💻' },
];

const currentOption = () => options.find(o => o.value === themeStore.theme);
// @archeon:endsection

// @archeon:section handlers
function handleSelect(value) {
  themeStore.setTheme(value);
  isOpen.value = false;
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
// @archeon:endsection
</script>

<!-- @archeon:section render -->
  <div ref="dropdownRef" class="relative inline-block">
    <button
      type="button"
      class="btn-outline flex items-center gap-2"
      @click="isOpen = !isOpen"
    >
      <span>{{ currentOption()?.icon }}</span>
      <span>{{ currentOption()?.label }}</span>
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-40 bg-surface rounded-md shadow-lg border border-border z-dropdown"
      >
        <button
          v-for="option in options"
          :key="option.value"
          type="button"
          class="w-full px-4 py-2 text-left text-sm flex items-center gap-2 hover:bg-surface-raised first:rounded-t-md last:rounded-b-md"
          :class="[
            themeStore.theme === option.value
              ? 'bg-primary-50 text-primary-600 dark:bg-primary-950 dark:text-primary-400'
              : 'text-content'
          ]"
          @click="handleSelect(option.value)"
        >
          <span>{{ option.icon }}</span>
          <span>{{ option.label }}</span>
          <svg
            v-if="themeStore.theme === option.value"
            class="h-4 w-4 ml-auto"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>
<!-- @archeon:endsection -->