import React from 'react';

const Loader = ({ show = false, label = 'Analyzing your report…' }) => {
  if (!show) return null;
  return (
    <div className="loader-overlay" role="alert" aria-live="assertive">
      <div className="loader-card">
        <div className="loader-ring">
          <div />
          <div />
          <div />
          <div />
        </div>
        <div className="loader-label">{label}</div>
        <div className="loader-sub">This may take a few moments</div>
      </div>
    </div>
  );
};

export default Loader;
