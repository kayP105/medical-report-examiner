import React from 'react';
import { useTheme } from './ThemeProvider';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar">
      <div className="nav-inner">
        <div className="brand brand--nav">
          <div className="brand-badge">MR</div>
          <div className="brand-text">
            <div className="brand-name">MED REPORT</div>
            <div className="brand-tag">Clinical Insights</div>
          </div>
        </div>

        <div className="nav-actions">
          <button
            className="btn btn-ghost"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title="Toggle theme"
          >
            {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
          </button>
          <a
            className="btn btn-outline"
            href="#upload"
            onClick={(e) => {
              const el = document.getElementById('upload');
              if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
            }}
          >
            Upload
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
