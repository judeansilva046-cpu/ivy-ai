// Type Definitions for Ivy AI Frontend

// Authentication
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  roles: string[]
  permissions: string[]
  createdAt: string
}

export interface AuthToken {
  accessToken: string
  refreshToken: string
  expiresIn: number
}

// Messages
export interface Message {
  id: string
  conversationId: string
  senderId: string
  senderName: string
  senderRole: 'user' | 'agent' | 'system'
  content: string
  contentType: 'text' | 'code' | 'markdown' | 'image'
  timestamp: string
  isRead: boolean
  reactions?: MessageReaction[]
  metadata?: Record<string, unknown>
}

export interface MessageReaction {
  emoji: string
  count: number
  userIds: string[]
}

export interface Conversation {
  id: string
  userId: string
  agentId: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

// Agents
export interface Agent {
  id: string
  name: string
  description: string
  type: 'core' | 'code' | 'research' | 'vision' | 'voice'
  capabilities: string[]
  status: 'active' | 'inactive' | 'maintenance'
  version: string
  icon?: string
  config?: Record<string, unknown>
}

export interface AgentCapability {
  name: string
  description: string
  inputSchema?: Record<string, unknown>
  outputSchema?: Record<string, unknown>
}

export interface AgentExecution {
  id: string
  agentId: string
  userId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input: Record<string, unknown>
  output?: Record<string, unknown>
  error?: string
  startTime: string
  endTime?: string
  duration?: number
}

// Tools
export interface Tool {
  id: string
  name: string
  description: string
  category: string
  enabled: boolean
  parameters?: ToolParameter[]
}

export interface ToolParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  description: string
  required: boolean
  default?: unknown
}

export interface ToolExecution {
  id: string
  toolId: string
  userId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input: Record<string, unknown>
  output?: unknown
  error?: string
  startTime: string
  endTime?: string
}

// Monitoring
export interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  requests: number
  errors: number
  uptime: number
  latency: number
}

export interface RequestLog {
  id: string
  method: string
  path: string
  statusCode: number
  duration: number
  timestamp: string
  userId?: string
  error?: string
}

export interface Alert {
  id: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  title: string
  description: string
  source: string
  timestamp: string
  resolved: boolean
  resolvedAt?: string
}

// UI State
export interface UIState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  selectedAgent?: string
  isLoading: boolean
  notifications: Notification[]
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  timestamp: string
}

// API Response
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// WebSocket Events
export interface WebSocketEvent {
  type: string
  data: unknown
  timestamp: string
}

export interface ChatWebSocketEvent extends WebSocketEvent {
  type: 'message' | 'typing' | 'user_joined' | 'user_left' | 'agent_status'
  data: Message | TypingIndicator | UserPresence | AgentStatus
}

export interface TypingIndicator {
  userId: string
  userName: string
  isTyping: boolean
}

export interface UserPresence {
  userId: string
  userName: string
  status: 'online' | 'offline' | 'away'
  lastSeen: string
}

export interface AgentStatus {
  agentId: string
  status: 'active' | 'inactive' | 'busy'
  processedRequests: number
  errorRate: number
}

// Form
export interface LoginForm {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterForm {
  name: string
  email: string
  password: string
  confirmPassword: string
  acceptTerms: boolean
}

export interface ChatMessage {
  content: string
  agentId?: string
}

// Pagination
export interface Pagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

// Sort
export interface Sort {
  field: string
  direction: 'asc' | 'desc'
}

// Filter
export interface Filter {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'in'
  value: unknown
}
