import React, { createContext, useState, useCallback, useEffect } from 'react';
import { connectionApi } from '../api/connectionApi';
import { useToast } from './ToastContext';

export const ConnectionsContext = createContext(null);

export function ConnectionsProvider({ children }) {
  const { showToast } = useToast();
  
  const [connections, setConnections] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // States for in-flight operations to show loaders on specific cards
  const [processingId, setProcessingId] = useState(null);
  const [processingType, setProcessingType] = useState(null); // 'sync' | 'delete'

  // Ref to track if we've already fetched once to prevent double fetching in dev mode
  const [hasFetched, setHasFetched] = useState(false);

  const fetchConnections = useCallback(async (force = false) => {
    if (!force && hasFetched) return; // Prevent unnecessary refetches
    
    setIsLoading(true);
    try {
      const data = await connectionApi.getConnections();
      setConnections(data.connections);
      setError(null);
      setHasFetched(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch connections');
    } finally {
      setIsLoading(false);
    }
  }, [hasFetched]);

  // Initial fetch on mount
  useEffect(() => {
    fetchConnections();
  }, [fetchConnections]);

  const addConnection = async (formData) => {
    try {
      const data = await connectionApi.addConnection(formData);
      showToast('Database connected successfully!', 'success');
      await fetchConnections(true); // Force refresh the list
      return data;
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to add connection', 'error');
      throw err;
    }
  };

  const deleteConnection = async (id) => {
    setProcessingId(id);
    setProcessingType('delete');
    try {
      await connectionApi.deleteConnection(id);
      showToast('Connection deleted', 'info');
      // Optimistic update
      setConnections(prev => prev.filter(c => c.id !== id));
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete connection', 'error');
    } finally {
      setProcessingId(null);
      setProcessingType(null);
    }
  };

  const syncConnection = async (id) => {
    setProcessingId(id);
    setProcessingType('sync');
    try {
      const data = await connectionApi.syncConnection(id);
      showToast('Database schema resynced successfully!', 'success');
      return data;
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to resync database', 'error');
    } finally {
      setProcessingId(null);
      setProcessingType(null);
    }
  };

  const value = {
    connections,
    isLoading,
    error,
    processingId,
    processingType,
    fetchConnections: () => fetchConnections(true), // Expose force fetch
    addConnection,
    deleteConnection,
    syncConnection
  };

  return (
    <ConnectionsContext.Provider value={value}>
      {children}
    </ConnectionsContext.Provider>
  );
}
