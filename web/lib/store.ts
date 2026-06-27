import { create } from 'zustand'
import { User, Message, Agent, Conversation, SystemMetrics, Alert } from './types'

// Auth Store
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  setUser: (user: User) => void
  setToken: (token: string) => void
  setAuthenticating: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: true }),
  setToken: (token) => {
    localStorage.setItem('auth_token', token)
    set({ token, isAuthenticated: true })
  },
  setAuthenticating: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  logout: () => {
    localStorage.removeItem('auth_token')
    set({ user: null, token: null, isAuthenticated: false })
  },
}))

// Chat Store
interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  currentAgent: Agent | null
  isLoading: boolean
  isTyping: boolean

  setConversations: (conversations: Conversation[]) => void
  setCurrentConversation: (conversation: Conversation) => void
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  setCurrentAgent: (agent: Agent | null) => void
  setLoading: (loading: boolean) => void
  setTyping: (typing: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  currentAgent: null,
  isLoading: false,
  isTyping: false,

  setConversations: (conversations) => set({ conversations }),
  setCurrentConversation: (conversation) => set({ currentConversation: conversation, messages: conversation.messages }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
    conversations: state.conversations.map((conv) =>
      conv.id === state.currentConversation?.id
        ? { ...conv, messages: [...conv.messages, message] }
        : conv
    ),
  })),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  setLoading: (loading) => set({ isLoading: loading }),
  setTyping: (typing) => set({ isTyping: typing }),
  clearMessages: () => set({ messages: [], currentConversation: null }),
}))

// Agents Store
interface AgentsState {
  agents: Agent[]
  selectedAgent: Agent | null
  isLoading: boolean

  setAgents: (agents: Agent[]) => void
  setSelectedAgent: (agent: Agent | null) => void
  setLoading: (loading: boolean) => void
  updateAgent: (agentId: string, agent: Partial<Agent>) => void
}

export const useAgentsStore = create<AgentsState>((set) => ({
  agents: [],
  selectedAgent: null,
  isLoading: false,

  setAgents: (agents) => set({ agents }),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
  setLoading: (loading) => set({ isLoading: loading }),
  updateAgent: (agentId, agent) =>
    set((state) => ({
      agents: state.agents.map((a) =>
        a.id === agentId ? { ...a, ...agent } : a
      ),
    })),
}))

// Monitoring Store
interface MonitoringState {
  metrics: SystemMetrics | null
  alerts: Alert[]
  isLoading: boolean

  setMetrics: (metrics: SystemMetrics) => void
  setAlerts: (alerts: Alert[]) => void
  addAlert: (alert: Alert) => void
  resolveAlert: (alertId: string) => void
  setLoading: (loading: boolean) => void
}

export const useMonitoringStore = create<MonitoringState>((set) => ({
  metrics: null,
  alerts: [],
  isLoading: false,

  setMetrics: (metrics) => set({ metrics }),
  setAlerts: (alerts) => set({ alerts }),
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts],
  })),
  resolveAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === alertId ? { ...a, resolved: true, resolvedAt: new Date().toISOString() } : a
      ),
    })),
  setLoading: (loading) => set({ isLoading: loading }),
}))

// UI Store
interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  notifications: Array<{ id: string; type: string; message: string }>

  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
  addNotification: (notification: { type: string; message: string }) => void
  removeNotification: (id: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  notifications: [],

  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    set({ theme })
  },
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: Math.random().toString() },
      ],
    })),
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}))
