import React from 'react';

export default function Button({ children, variant = 'primary', isLoading, fullWidth, className = '', ...props }) {
  const baseClass = `btn btn--${variant}`;
  const widthClass = fullWidth ? 'btn--full' : '';
  const loadingClass = isLoading ? 'btn--loading' : '';
  
  return (
    <button 
      className={`${baseClass} ${widthClass} ${loadingClass} ${className}`.trim()} 
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? <span className="btn-spinner" /> : children}
    </button>
  );
}
