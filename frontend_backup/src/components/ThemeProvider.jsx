import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const ThemeContext = createContext({
  theme: 'dark',
  setTheme: () => {},
  toggleTheme: () => {}
});

export const ThemeProvider = ({ children }) => {
  const getInitial = () => {
    const stored = localStorage.getItem('mr_theme');
    if (stored === 'light' || stored === 'dark') return stored;
    return 'dark';
  };

  const [theme, setTheme] = useState(getInitial);

  useEffect(() => {
    localStorage.setItem('mr_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const value = useMemo(() => ({
    theme,
    setTheme,
    toggleTheme: () => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
  }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => useContext(ThemeContext);
