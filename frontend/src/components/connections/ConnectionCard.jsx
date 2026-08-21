import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../common/Button';

export default function ConnectionCard({ connection, onDelete, onSync, isDeleting, isSyncing }) {
  const dateStr = new Date(connection.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  return (
    <div className="connection-card">
      <div className="connection-card-header">
        <h3 className="connection-card-title">{connection.nickname}</h3>
        <span className="connection-card-status">
          <span className="status-dot"></span> Active
        </span>
      </div>
      
      <div className="connection-card-body">
        <p className="connection-card-meta">Added on {dateStr}</p>
      </div>

      <div className="connection-card-actions">
        <div className="connection-card-actions-left">
          <button 
            className="action-btn text-error" 
            onClick={() => onDelete(connection.id)}
            disabled={isDeleting || isSyncing}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
          <button 
            className="action-btn text-muted" 
            onClick={() => onSync(connection.id)}
            disabled={isDeleting || isSyncing}
          >
            {isSyncing ? 'Syncing...' : 'Resync Schema'}
          </button>
        </div>
        <Link to={`/connections/${connection.id}`} className="btn btn--primary btn--sm">
          Query DB
        </Link>
      </div>
    </div>
  );
}
