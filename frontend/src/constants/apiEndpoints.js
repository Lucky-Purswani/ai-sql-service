const BASE_URL = 'http://127.0.0.1:8000/api'

export const API_ENDPOINTS = {
  // Auth
  SIGNUP: `${BASE_URL}/auth/signup`,
  LOGIN: `${BASE_URL}/auth/login`,
  VERIFY_EMAIL: `${BASE_URL}/auth/verify-email`,
  REFRESH_TOKEN: `${BASE_URL}/auth/refresh`,

  // Connections
  CONNECTIONS: `${BASE_URL}/connections`,

  // Query
  QUERY: `${BASE_URL}/query/`,
  QUERY_EXPORT: `${BASE_URL}/query/export`,
}
