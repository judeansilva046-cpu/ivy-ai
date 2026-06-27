# 🎨 ETAPA 14: Frontend Development - Setup Guide

## Project Structure

```
web/
├── app/
│   ├── layout.tsx           (Root layout)
│   ├── page.tsx             (Home/Chat page)
│   ├── chat/
│   │   ├── page.tsx         (Chat interface)
│   │   └── layout.tsx       (Chat layout)
│   ├── agents/
│   │   ├── page.tsx         (Agent management)
│   │   └── [id].tsx         (Agent details)
│   ├── admin/
│   │   ├── dashboard.tsx    (Admin dashboard)
│   │   ├── users.tsx        (User management)
│   │   └── monitoring.tsx   (System monitoring)
│   └── auth/
│       ├── login.tsx        (Login page)
│       └── register.tsx     (Register page)
│
├── components/
│   ├── ChatInterface.tsx     (Main chat UI)
│   ├── MessageList.tsx       (Message display)
│   ├── InputBox.tsx          (Message input)
│   ├── AgentCard.tsx         (Agent display)
│   ├── Dashboard.tsx         (Dashboard widget)
│   ├── Sidebar.tsx           (Navigation)
│   └── Navbar.tsx            (Top bar)
│
├── lib/
│   ├── api.ts               (API client)
│   ├── websocket.ts         (WebSocket handler)
│   ├── auth.ts              (Authentication)
│   ├── store.ts             (Zustand store)
│   └── types.ts             (Type definitions)
│
├── styles/
│   ├── globals.css          (Global styles)
│   └── tailwind.css         (Tailwind config)
│
├── public/
│   ├── favicon.ico
│   └── logo.svg
│
├── next.config.js           (Next.js config)
├── tsconfig.json            (TypeScript config)
├── tailwind.config.js       (Tailwind config)
├── postcss.config.js        (PostCSS config)
└── package.json             (Dependencies)
```

## Technology Stack

- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Real-time:** Socket.io
- **Icons:** Lucide React
- **Notifications:** React Hot Toast
- **Date:** date-fns
- **Markdown:** markdown-it
- **Testing:** Jest + React Testing Library

## Features

### Authentication
- JWT-based login/register
- Protected routes
- Session management
- OAuth2 integration ready

### Chat Interface
- Real-time messaging (WebSocket)
- Message history
- Markdown support with syntax highlighting
- File uploads
- Typing indicators
- Read receipts

### Agent Management
- List all agents
- View agent capabilities
- Execute agent actions
- Agent performance metrics
- Enable/disable agents

### Admin Dashboard
- System monitoring (CPU, Memory, Disk)
- User management
- Request logs
- Error tracking
- Performance metrics
- Alert management

### Responsive Design
- Mobile-first approach
- Dark mode support
- Accessibility (WCAG 2.1)
- Progressive Web App (PWA) ready

## Setup Instructions

### 1. Install Dependencies
```bash
cd web
npm install
```

### 2. Environment Variables
```bash
cp .env.example .env.local
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=Ivy AI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 3. Development Server
```bash
npm run dev
```

Access at `http://localhost:3000`

### 4. Build for Production
```bash
npm run build
npm start
```

### 5. Run Tests
```bash
npm test
npm run test:coverage
```

## Project Components

### Authentication Store
```typescript
interface AuthState {
  isAuthenticated: boolean
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}
```

### Chat Store
```typescript
interface ChatState {
  messages: Message[]
  currentAgent: Agent | null
  isLoading: boolean
  addMessage: (message: Message) => void
  setCurrentAgent: (agent: Agent) => void
  clearMessages: () => void
}
```

### API Client
```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const apiClient = {
  auth: { login, register, logout },
  chat: { sendMessage, getHistory },
  agents: { list, getDetails, execute },
  admin: { getDashboard, getUsers, getMetrics }
}
```

### WebSocket Handler
```typescript
export const useWebSocket = () => {
  const socket = io(process.env.NEXT_PUBLIC_WS_URL)
  
  return {
    connect: () => socket.connect(),
    disconnect: () => socket.disconnect(),
    on: (event, callback) => socket.on(event, callback),
    emit: (event, data) => socket.emit(event, data)
  }
}
```

## Styling with Tailwind

### Color Scheme
```css
Primary: #3B82F6 (Blue)
Secondary: #10B981 (Green)
Danger: #EF4444 (Red)
Dark: #1F2937 (Dark Gray)
```

### Responsive Breakpoints
```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

## Performance Optimization

- Next.js Image optimization
- Code splitting (dynamic imports)
- CSS compression
- JavaScript minification
- Caching strategies
- Lazy loading components

## Security

- HTTPS enforcement (production)
- CORS configuration
- XSS protection (Content Security Policy)
- CSRF token validation
- Secure cookies (HttpOnly, SameSite)
- Rate limiting on client

## Testing Strategy

### Unit Tests
- Component rendering
- Store actions
- Utility functions

### Integration Tests
- Page navigation
- Form submissions
- API integration

### E2E Tests (Playwright)
- User workflows
- Chat interactions
- Authentication flows

## Deployment

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose
```yaml
web:
  build: ./web
  ports:
    - "3000:3000"
  environment:
    NEXT_PUBLIC_API_URL: http://localhost:8000
    NEXT_PUBLIC_WS_URL: ws://localhost:8000
```

### Kubernetes
See `k8s/web-deployment.yaml`

## Next Steps

1. ✅ Project setup (Next.js + dependencies)
2. ✅ TypeScript configuration
3. ✅ Tailwind CSS setup
4. ✅ Authentication pages
5. ✅ Chat interface
6. ✅ Agent management
7. ✅ Admin dashboard
8. ✅ API integration
9. ✅ WebSocket integration
10. ✅ Testing setup
11. ✅ Docker deployment
12. ✅ Kubernetes deployment

---

*Ivy AI Frontend Development Guide*
*ETAPA 14 - Next.js React Application*
