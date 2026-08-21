import { useState } from 'react';
import { queryApi } from '../api/queryApi';
import { useToast } from '../context/ToastContext';

export function useQuery() {
  const { showToast } = useToast();
  
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeQuery = async (connectionId, question) => {
    setIsLoading(true);
    setError(null);
    setData(null); // Clear previous results while loading

    try {
      const response = await queryApi.executeQuery({
        connection_id: connectionId,
        question: question
      });
      setData(response);
      return response;
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'An error occurred while running the query';
      setError(errMsg);
      showToast(errMsg, 'error');
      // Don't re-throw — error is stored in state and shown in UI
    } finally {
      setIsLoading(false);
    }
  };

  const resetQuery = () => {
    setData(null);
    setError(null);
    setIsLoading(false);
  };

  return {
    data,
    isLoading,
    error,
    executeQuery,
    resetQuery
  };
}
