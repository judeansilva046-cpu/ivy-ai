# Jarvis AI - Frontend Web

Frontend Next.js 14 para a plataforma Jarvis AI Enterprise Platform.

## 🎯 Características

- ✅ Chat interface com histórico de conversas
- ✅ Real-time message updates
- ✅ Document upload and management
- ✅ System status monitoring
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode support
- ✅ TypeScript support
- ✅ Tailwind CSS styling

## 📋 Pré-requisitos

- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend Jarvis AI rodando (http://127.0.0.1:8000)

## 🚀 Início Rápido

### 1. Instalar dependências

```bash
cd C:\JarvisAI\web
npm install
```

### 2. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env.local

# Editar .env.local se necessário
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. Iniciar servidor de desenvolvimento

```bash
npm run dev
```

Acesse http://localhost:3000

## 📁 Estrutura do Projeto

```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Chat page
│   ├── globals.css     # Global styles
│   ├── documents/      # Documents management
│   └── settings/       # Settings page
├── components/         # React components
│   ├── ChatMessage.tsx
│   ├── ChatBox.tsx
│   └── Sidebar.tsx
└── lib/               # Utilities
    ├── api.ts         # API client
    └── store.ts       # Zustand store
```

## 🔧 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

## 🎨 Customização

### Cores

Edite `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      primary: '#6366f1',
      secondary: '#8b5cf6',
      // ...
    }
  }
}
```

### Fonts

Edite `src/app/globals.css`:

```css
body {
  font-family: 'Your Font', sans-serif;
}
```

## 🔌 API Integration

O frontend se conecta ao backend em:
- `NEXT_PUBLIC_API_URL` (padrão: http://127.0.0.1:8000)

Endpoints principais:
- `POST /chat/` - Send message
- `POST /documents/ingest` - Upload documents
- `GET /documents/status` - Get document stats
- `GET /system/status` - Get system status

## 📱 Responsive Design

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🌙 Dark Mode

Dark mode é automaticamente detectado pelo sistema operacional.
Para forçar dark mode, adicione no localStorage:

```js
localStorage.setItem('theme', 'dark');
```

## 🧪 Testing

```bash
npm run type-check  # TypeScript check
npm run lint        # ESLint
```

## 📦 Build & Deploy

### Build para produção

```bash
npm run build
npm start
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run lint and type-check
4. Submit PR

## 📄 License

MIT

## 📞 Support

Para suporte, abra uma issue no repositório.
