// @archeon:file
// @glyph STO:Theme
// @intent Theme state management with light/dark/system modes and color themes (Zustand)
// @chain @v1 TSK:toggle_theme => CMP:ThemeToggle => STO:Theme => OUT:theme_changed

// @archeon:section imports
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
// @archeon:endsection

// @archeon:section state
// === THEME SYSTEM ARCHITECTURE ===
// This store manages TWO separate concerns:
// 1. MODE: Light/Dark/System - controls the brightness scheme
// 2. COLOR THEME: Project-specific color palettes that override --color-primary-* variables
//
// The color theme works by adding a CSS class to the document root.
// These classes override the --color-primary-* CSS variables.
// See: archeon/templates/_config/theme-presets.css for preset examples.
//
// Usage in components:
//   const { colorTheme, setColorTheme } = useTheme()
//   setColorTheme('purple') // Switches to purple theme
//
// The theme tokens propagate through:
//   design-tokens.json -> theme-presets.css -> STO:Theme -> CSS variables -> components
//
// === CUSTOMIZATION ===
// The COLOR_THEMES and COLOR_THEME_CLASSES below are EXAMPLES.
// Each project should define its own themes based on:
//   1. The color palettes in design-tokens.json
//   2. The theme classes in theme-presets.css
// Update these constants to match your project's design system.

// Light/Dark mode constants (these are standard)
const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
};

// =============================================================================
// COLOR THEMES - CUSTOMIZE PER PROJECT
// =============================================================================
// These are example themes. Update to match your project's theme-presets.css.
// The keys become the values stored/used in code (e.g., 'blue', 'purple').
// Add/remove themes as needed for your design system.
const COLOR_THEMES = {
  BLUE: 'blue',      // Example: maps to .theme-ocean
  PURPLE: 'purple',  // Example: maps to .theme-royal
  GREEN: 'green',    // Example: maps to .theme-forest
};

// Maps theme values to CSS class names from theme-presets.css
// Update this when you add/modify themes in theme-presets.css
const COLOR_THEME_CLASSES = {
  [COLOR_THEMES.BLUE]: 'theme-ocean',
  [COLOR_THEMES.PURPLE]: 'theme-royal',
  [COLOR_THEMES.GREEN]: 'theme-forest',
};
// =============================================================================
// @archeon:endsection

// @archeon:section helpers
// Get system preference for light/dark
const getSystemTheme = () => {
  if (typeof window === 'undefined') return THEMES.LIGHT;
  return window.matchMedia('(prefers-color-scheme: dark)').matches 
    ? THEMES.DARK 
    : THEMES.LIGHT;
};

// Apply light/dark mode to DOM
const applyMode = (resolvedTheme) => {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(resolvedTheme);
  root.style.colorScheme = resolvedTheme;
};

// Apply color theme to DOM (swaps --color-primary-* variables)
const applyColorTheme = (colorTheme) => {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  // Remove all color theme classes
  Object.values(COLOR_THEME_CLASSES).forEach(cls => root.classList.remove(cls));
  // Add the selected theme class
  const themeClass = COLOR_THEME_CLASSES[colorTheme] || COLOR_THEME_CLASSES[COLOR_THEMES.BLUE];
  root.classList.add(themeClass);
};
// @archeon:endsection

// @archeon:section actions
// Create theme store with persistence
export const useThemeStore = create(
  persist(
    (set, get) => ({
      // === State ===
      theme: THEMES.SYSTEM,           // 'light' | 'dark' | 'system'
      resolvedTheme: getSystemTheme(), // Actual applied mode
      colorTheme: COLOR_THEMES.BLUE,  // 'blue' | 'purple' | 'green'
      
      // === Actions: Light/Dark Mode ===
      setTheme: (theme) => {
        const resolvedTheme = theme === THEMES.SYSTEM ? getSystemTheme() : theme;
        applyMode(resolvedTheme);
        set({ theme, resolvedTheme });
      },
      
      toggleTheme: () => {
        const { resolvedTheme } = get();
        const newTheme = resolvedTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
        applyMode(newTheme);
        set({ theme: newTheme, resolvedTheme: newTheme });
      },
      
      // === Actions: Color Theme ===
      setColorTheme: (colorTheme) => {
        applyColorTheme(colorTheme);
        set({ colorTheme });
      },
      
      cycleColorTheme: () => {
        const { colorTheme } = get();
        const themes = Object.values(COLOR_THEMES);
        const currentIndex = themes.indexOf(colorTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        const newColorTheme = themes[nextIndex];
        applyColorTheme(newColorTheme);
        set({ colorTheme: newColorTheme });
      },
      
      // === Initialization ===
      initTheme: () => {
        const { theme, colorTheme } = get();
        const resolvedTheme = theme === THEMES.SYSTEM ? getSystemTheme() : theme;
        applyMode(resolvedTheme);
        applyColorTheme(colorTheme);
        set({ resolvedTheme });
        
        // Listen for system preference changes
        if (typeof window !== 'undefined') {
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          mediaQuery.addEventListener('change', (e) => {
            const { theme } = get();
            if (theme === THEMES.SYSTEM) {
              const newResolvedTheme = e.matches ? THEMES.DARK : THEMES.LIGHT;
              applyMode(newResolvedTheme);
              set({ resolvedTheme: newResolvedTheme });
            }
          });
        }
      },
      
      // === Computed-like getters ===
      isDark: () => get().resolvedTheme === THEMES.DARK,
      isLight: () => get().resolvedTheme === THEMES.LIGHT,
      isSystem: () => get().theme === THEMES.SYSTEM,
    }),
    {
      name: 'archeon-theme', // localStorage key
      partialize: (state) => ({ 
        theme: state.theme,
        colorTheme: state.colorTheme 
      }), // Persist both mode and color theme
    }
  )
);
// @archeon:endsection

// @archeon:section selectors
// Export constants
export { THEMES, COLOR_THEMES };

// Convenience hook for React components
export const useTheme = () => {
  const store = useThemeStore();
  return {
    // Mode state
    theme: store.theme,
    resolvedTheme: store.resolvedTheme,
    setTheme: store.setTheme,
    toggleTheme: store.toggleTheme,
    isDark: store.isDark(),
    isLight: store.isLight(),
    isSystem: store.isSystem(),
    // Color theme state
    colorTheme: store.colorTheme,
    setColorTheme: store.setColorTheme,
    cycleColorTheme: store.cycleColorTheme,
    // Init
    initTheme: store.initTheme,
  };
};
// @archeon:endsection

export default useThemeStore;
