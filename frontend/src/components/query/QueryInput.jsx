import React, { useState, useRef, useEffect } from 'react';

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize: starts at 1 row, caps at 3 rows on mobile
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    // lineHeight ~24px, cap at 3 rows = 72px on mobile, 6 rows on desktop
    const isMobile = window.innerWidth < 768;
    const maxH = isMobile ? 72 : 160;
    el.style.height = `${Math.min(el.scrollHeight, maxH)}px`;
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="query-input-form" onSubmit={handleSubmit}>
      <div className="query-input-wrapper">
        <textarea
          ref={textareaRef}
          className="query-input-textarea"
          placeholder="Ask a question about your data..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />
        <button
          type="submit"
          className="query-input-submit"
          disabled={!query.trim() || isLoading}
          aria-label="Submit query"
        >
          {isLoading ? (
            <span className="query-btn-spinner" />
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
    </form>
  );
}
