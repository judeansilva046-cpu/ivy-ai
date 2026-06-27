import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export interface ChatRequest {
  query: string;
  session_id: string;
}

export interface ChatResponse {
  success: boolean;
  query: string;
  response: string;
  context_used: number;
  timestamp: string;
  model: string;
}

export const chatAPI = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat/', data);
    return response.data;
  },

  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getSystemStatus: async () => {
    const response = await apiClient.get('/system/status');
    return response.data;
  },

  getDocumentsStatus: async () => {
    const response = await apiClient.get('/documents/status');
    return response.data;
  },

  uploadDocuments: async (formData: FormData) => {
    const response = await apiClient.post('/documents/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
