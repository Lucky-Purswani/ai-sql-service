import React, { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '../hooks/useQuery';
import { useConnections } from '../hooks/useConnections';
import { queryApi } from '../api/queryApi';
import QueryInput from '../components/query/QueryInput';
import DataTable from '../components/table/DataTable';
import '../styles/query.css';

export default function QueryPage() {
  const { id: connectionId } = useParams();
  const { connections } = useConnections();
  const { data, isLoading, error, executeQuery } = useQuery();
  const resultsEndRef = useRef(null);
  const [isExporting, setIsExporting] = useState(false);

  const connection = connections.find(c => c.id === connectionId);
  const nickname = connection ? connection.nickname : 'Database';

  // Auto-scroll to the latest result or error
  useEffect(() => {
    if ((data || error) && resultsEndRef.current) {
      resultsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [data, error]);

  const handleSubmit = (question) => {
    executeQuery(connectionId, question);
  };

  const handleExport = async () => {
    if (!data) return;
    setIsExporting(true);
    try {
      const filename = `${nickname.replace(/\s+/g, '_')}_query_${Date.now()}`;
      await queryApi.exportQueryAsCsv(connectionId, data.sql_used, filename);
    } catch (err) {
      // toast is not used here to keep it simple — browser will show its own download error
      console.error('Export failed', err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="query-layout">

      {/* Top bar — never scrolls */}
      <header className="query-header">
        <div className="query-header-left">
          <Link to="/dashboard" className="btn-back">← Back</Link>
          <h2 className="query-title">
            Querying: <span>{nickname}</span>
          </h2>
        </div>
      </header>

      {/* Only this area scrolls */}
      <main className="query-content">

        {/* Empty/welcome state */}
        {!data && !error && !isLoading && (
          <div className="query-empty">
            <div className="query-empty-icon">🗄️</div>
            <h3>Ask anything about your data</h3>
            <p>
              Type a question below. AI SQL will translate it into a
              read-only query and instantly return the results.
            </p>
          </div>
        )}

        {/* Loading skeleton */}
        {isLoading && (
          <div className="query-loading">
            <span className="query-loading-dot" />
            <span className="query-loading-dot" />
            <span className="query-loading-dot" />
          </div>
        )}

        {/* Friendly out-of-context response */}
        {error && !isLoading && (
          <div className="query-ai-response">
            <div className="query-ai-avatar">AI</div>
            <div className="query-ai-bubble">
              <p className="query-ai-text">
                {error.startsWith('ERROR:') || error.includes('Cannot answer')
                  ? "I couldn't find anything in your database that matches that question. Try asking something more specific to your schema, like table names, column names, or relationships."
                  : error
                }
              </p>
            </div>
          </div>
        )}

        {/* Successful result */}
        {data && !isLoading && (
          <div className="query-result-block">
            {/* AI Summary */}
            <div className="query-summary">
              <div className="query-summary-icon">✨</div>
              <div className="query-summary-text">{data.summary}</div>
            </div>

            {/* Generated SQL */}
            <div className="query-sql-container">
              <h4 className="query-sql-title">Generated SQL</h4>
              <pre className="query-sql-code"><code>{data.sql_used}</code></pre>
            </div>

            {/* Data Table */}
            <DataTable
              columns={data.columns}
              rows={data.sample_rows}
              totalRows={data.total_rows}
            />

            {/* Download Button */}
            <div className="query-export-row">
              <button
                className="query-export-btn"
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting ? (
                  <><span className="query-btn-spinner" style={{width:'14px',height:'14px',borderColor:'rgba(0,0,0,0.2)',borderTopColor:'black'}} /> Preparing CSV...</>
                ) : (
                  <>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7 10 12 15 17 10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download full data as CSV ({data.total_rows.toLocaleString()} rows)
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        <div ref={resultsEndRef} />
      </main>

      {/* Fixed input anchored to bottom */}
      <footer className="query-footer">
        <div className="query-footer-inner">
          <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </footer>
    </div>
  );
}
