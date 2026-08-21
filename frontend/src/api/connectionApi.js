import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

export const connectionApi = {
  getConnections: async () => {
    const response = await axiosClient.get(API_ENDPOINTS.CONNECTIONS);
    return response.data; // { connections: [] }
  },

  addConnection: async (data) => {
    // data: { nickname, db_url }
    const response = await axiosClient.post(API_ENDPOINTS.CONNECTIONS, data);
    return response.data;
  },

  deleteConnection: async (id) => {
    const response = await axiosClient.delete(`${API_ENDPOINTS.CONNECTIONS}/${id}`);
    return response.data;
  },

  syncConnection: async (id) => {
    const response = await axiosClient.post(`${API_ENDPOINTS.CONNECTIONS}/${id}/sync`);
    return response.data;
  }
};
