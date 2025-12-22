// @archeon:file
// @glyph CMP:ThemeToggle
// @intent Dark/light mode toggle button with icon switching (React)
// @chain @v1 TSK:toggle_theme => CMP:ThemeToggle => STO:Theme => OUT:theme_changed

// @archeon:section imports
import React from 'react';
import { useTheme, THEMES } from '@/stores/themeStore';
// @archeon:endsection

// @archeon:section render
export function ThemeToggle({ className = '' }) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Simple toggle button */}
      <button
        type="button"
        onClick={toggleTheme}
        className="btn-ghost p-2 rounded-md"
        aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
      >
        {resolvedTheme === 'dark' ? (
          // Sun icon for dark mode (click to switch to light)
          <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          // Moon icon for light mode (click to switch to dark)
          <svg className="h-5 w-5 text-content-secondary" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        )}
      </button>
    </div>
  );
}
// @archeon:endsection

// @archeon:section handlers
// Extended version with dropdown for light/dark/system
export function ThemeSelector({ className = '' }) {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = React.useState(false);

  const options = [
    { value: THEMES.LIGHT, label: 'Light', icon: '☀️' },
    { value: THEMES.DARK, label: 'Dark', icon: '🌙' },
    { value: THEMES.SYSTEM, label: 'System', icon: '💻' },
  ];

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="btn-outline flex items-center gap-2"
      >
        <span>{options.find(o => o.value === theme)?.icon}</span>
        <span>{options.find(o => o.value === theme)?.label}</span>
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-surface rounded-md shadow-lg border border-border z-dropdown animate-scale-in">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                setTheme(option.value);
                setIsOpen(false);
              }}
              className={`w-full px-4 py-2 text-left text-sm flex items-center gap-2 hover:bg-surface-raised first:rounded-t-md last:rounded-b-md ${
                theme === option.value ? 'bg-primary-50 text-primary-600 dark:bg-primary-950' : 'text-content'
              }`}
            >
              <span>{option.icon}</span>
              <span>{option.label}</span>
              {theme === option.value && (
                <svg className="h-4 w-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
// @archeon:endsection

export default ThemeToggle;
