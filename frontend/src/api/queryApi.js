import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

export const queryApi = {
  /**
   * Executes a natural language query against a specific database connection.
   */
  executeQuery: async (payload) => {
    const response = await axiosClient.post(API_ENDPOINTS.QUERY, payload);
    return response.data;
  },

  /**
   * Streams the FULL query result as a CSV file download.
   * @param {string} connectionId
   * @param {string} sqlUsed - The already-validated SQL from a previous query
   * @param {string} filename - Suggested filename (without extension)
   */
  exportQueryAsCsv: async (connectionId, sqlUsed, filename = 'export') => {
    const response = await axiosClient.post(
      API_ENDPOINTS.QUERY_EXPORT,
      { connection_id: connectionId, sql_used: sqlUsed, filename },
      { responseType: 'blob' } // receive raw binary stream
    );

    // Trigger browser download
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${filename}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};
