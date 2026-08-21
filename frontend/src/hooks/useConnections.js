import { useContext } from 'react';
import { ConnectionsContext } from '../context/ConnectionsContext';

export function useConnections() {
  const context = useContext(ConnectionsContext);
  if (!context) {
    throw new Error('useConnections must be used within a ConnectionsProvider');
  }
  return context;
}
