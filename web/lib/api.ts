import axios, { AxiosInstance, AxiosError } from 'axios'
import { ApiResponse, PaginatedResponse, User, Message, Agent, AgentExecution, SystemMetrics } from './types'
import { useAuthStore } from './store'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await axiosInstance.post<ApiResponse<{ token: string; user: User }>>('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  register: async (name: string, email: string, password: string) => {
    const response = await axiosInstance.post<ApiResponse<User>>('/auth/register', {
      name,
      email,
      password,
    })
    return response.data
  },

  logout: async () => {
    const response = await axiosInstance.post<ApiResponse<null>>('/auth/logout')
    return response.data
  },

  me: async () => {
    const response = await axiosInstance.get<ApiResponse<User>>('/auth/me')
    return response.data
  },

  refreshToken: async () => {
    const response = await axiosInstance.post<ApiResponse<{ token: string }>>('/auth/refresh')
    return response.data
  },
}

// Chat API
export const chatAPI = {
  sendMessage: async (conversationId: string, content: string, agentId?: string) => {
    const response = await axiosInstance.post<ApiResponse<Message>>('/chat/send', {
      conversationId,
      content,
      agentId,
    })
    return response.data
  },

  getHistory: async (conversationId: string, page: number = 1, limit: number = 50) => {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<Message>>>(`/chat/history/${conversationId}`, {
      params: { page, limit },
    })
    return response.data
  },

  getConversations: async (page: number = 1, limit: number = 20) => {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<any>>>('/chat/conversations', {
      params: { page, limit },
    })
    return response.data
  },

  createConversation: async (agentId: string) => {
    const response = await axiosInstance.post<ApiResponse<any>>('/chat/conversations', {
      agentId,
    })
    return response.data
  },

  deleteConversation: async (conversationId: string) => {
    const response = await axiosInstance.delete<ApiResponse<null>>(`/chat/conversations/${conversationId}`)
    return response.data
  },
}

// Agents API
export const agentsAPI = {
  list: async () => {
    const response = await axiosInstance.get<ApiResponse<Agent[]>>('/agent/list')
    return response.data
  },

  getDetails: async (agentId: string) => {
    const response = await axiosInstance.get<ApiResponse<Agent>>(`/agent/${agentId}/info`)
    return response.data
  },

  execute: async (agentId: string, input: Record<string, unknown>) => {
    const response = await axiosInstance.post<ApiResponse<AgentExecution>>(`/agent/${agentId}/execute`, {
      input,
    })
    return response.data
  },

  getStatus: async (agentId: string) => {
    const response = await axiosInstance.get<ApiResponse<any>>(`/agent/${agentId}/status`)
    return response.data
  },
}

// Tools API
export const toolsAPI = {
  list: async () => {
    const response = await axiosInstance.get<ApiResponse<any[]>>('/tool/list')
    return response.data
  },

  execute: async (toolId: string, params: Record<string, unknown>) => {
    const response = await axiosInstance.post<ApiResponse<any>>(`/tool/${toolId}/execute`, {
      params,
    })
    return response.data
  },
}

// Admin API
export const adminAPI = {
  getDashboard: async () => {
    const response = await axiosInstance.get<ApiResponse<any>>('/admin/dashboard')
    return response.data
  },

  getSystemStatus: async () => {
    const response = await axiosInstance.get<ApiResponse<SystemMetrics>>('/admin/system-status')
    return response.data
  },

  getHealth: async () => {
    const response = await axiosInstance.get<ApiResponse<any>>('/admin/health')
    return response.data
  },

  getUsers: async (page: number = 1, limit: number = 20) => {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<User>>>('/admin/users', {
      params: { page, limit },
    })
    return response.data
  },

  getLogs: async (page: number = 1, limit: number = 50) => {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<any>>>('/admin/logs', {
      params: { page, limit },
    })
    return response.data
  },

  getMetrics: async () => {
    const response = await axiosInstance.get<ApiResponse<any>>('/admin/metrics')
    return response.data
  },
}

// Vision API
export const visionAPI = {
  analyze: async (imageData: string, operation: string) => {
    const response = await axiosInstance.post<ApiResponse<any>>('/vision/analyze', {
      imageData,
      operation,
    })
    return response.data
  },

  uploadAndAnalyze: async (file: File, operation: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('operation', operation)

    const response = await axiosInstance.post<ApiResponse<any>>('/vision/upload-and-analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

// Audio API
export const audioAPI = {
  speechToText: async (audioData: string, language: string = 'pt') => {
    const response = await axiosInstance.post<ApiResponse<any>>('/audio/speech-to-text', {
      audioData,
      language,
    })
    return response.data
  },

  textToSpeech: async (text: string, language: string = 'pt') => {
    const response = await axiosInstance.post<ApiResponse<any>>('/audio/text-to-speech', {
      text,
      language,
    })
    return response.data
  },
}

// Export axios instance for custom requests
export default axiosInstance
