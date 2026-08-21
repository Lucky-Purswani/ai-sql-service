import axios from 'axios';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

// Create base instance
const axiosClient = axios.create({
  withCredentials: true, // IMPORTANT: Allows cookies (refresh_token) to be sent automatically
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach access token if available
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s and Token Rotation
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't already retried this request
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // Auth endpoints (login, signup, verify) should NEVER trigger the refresh flow.
      // Their 401s mean "wrong credentials" — pass them straight through to the caller.
      const isAuthEndpoint = [
        API_ENDPOINTS.LOGIN,
        API_ENDPOINTS.SIGNUP,
        API_ENDPOINTS.VERIFY_EMAIL,
        API_ENDPOINTS.REFRESH_TOKEN,
      ].some(url => originalRequest.url === url);

      if (isAuthEndpoint) {
        // For the refresh endpoint specifically, also clear storage and redirect to login
        if (originalRequest.url === API_ENDPOINTS.REFRESH_TOKEN) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error); // Let the caller handle it (show toast, etc.)
      }

      if (isRefreshing) {
        // If already refreshing, queue this request until refresh is done
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return axiosClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh the token. 
        // The HttpOnly cookie is sent automatically because of `withCredentials: true`.
        const { data } = await axios.post(
          API_ENDPOINTS.REFRESH_TOKEN, 
          {}, 
          { withCredentials: true }
        );
        
        const newAccessToken = data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        
        // Setup new token for current request
        axiosClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        
        processQueue(null, newAccessToken);
        return axiosClient(originalRequest);
        
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;
