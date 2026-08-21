import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import axios from 'axios';

export const authApi = {
  signup: async (data) => {
    // data: { email, password, password_confirm }
    const response = await axiosClient.post(API_ENDPOINTS.SIGNUP, data);
    return response.data;
  },

  verifyEmail: async (data) => {
    // data: { email, otp }
    const response = await axiosClient.post(API_ENDPOINTS.VERIFY_EMAIL, data);
    return response.data;
  },

  login: async (data) => {
    // data: { email, password }
    const response = await axiosClient.post(API_ENDPOINTS.LOGIN, data);
    return response.data; // { access_token, token_type }
  },

  // Used on initial load if we don't have a valid access token in memory
  // but might have a valid refresh token cookie.
  silentRefresh: async () => {
    // We use a raw axios instance here to avoid infinite loops with our interceptor
    const response = await axios.post(
      API_ENDPOINTS.REFRESH_TOKEN,
      {},
      { withCredentials: true }
    );
    return response.data;
  },
};
