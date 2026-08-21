import React from 'react';
import ConnectionCard from './ConnectionCard';

export default function ConnectionList({ connections, onDelete, onSync, processingId, processingType }) {
  if (!connections || connections.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🗄️</div>
        <h3 className="empty-state-title">No databases connected</h3>
        <p className="empty-state-desc">
          Add your first PostgreSQL database to start asking questions in natural language.
        </p>
      </div>
    );
  }

  return (
    <div className="connection-grid">
      {connections.map(conn => (
        <ConnectionCard 
          key={conn.id} 
          connection={conn}
          onDelete={onDelete}
          onSync={onSync}
          isDeleting={processingId === conn.id && processingType === 'delete'}
          isSyncing={processingId === conn.id && processingType === 'sync'}
        />
      ))}
    </div>
  );
}
