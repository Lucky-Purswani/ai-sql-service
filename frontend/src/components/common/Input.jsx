import React from 'react';

export default function Input({ label, error, ...props }) {
  return (
    <div className="input-group">
      {label && <label className="input-label">{label}</label>}
      <input 
        className={`input-field ${error ? 'input-field--error' : ''}`} 
        {...props} 
      />
      {error && <span className="input-error">{error}</span>}
    </div>
  );
}
