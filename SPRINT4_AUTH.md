# 🔐 Sprint 4 - Autenticação JWT Criado!

## ✅ Backend Implementado

### Models
- ✅ **User model** com SQLAlchemy
  - id, email, username, hashed_password
  - full_name, is_active, is_admin
  - created_at, updated_at, last_login

### Security
- ✅ **Password hashing** com bcrypt
- ✅ **JWT tokens** com expiration
- ✅ **Token refresh** logic
- ✅ **Access & Refresh tokens**

### API Routes
- ✅ `POST /auth/register` - Criar conta
- ✅ `POST /auth/login` - Fazer login
- ✅ `POST /auth/refresh` - Renovar token
- ✅ `GET /auth/me` - Usuário atual

### Database
- ✅ SQLAlchemy ORM
- ✅ PostgreSQL integration
- ✅ Auto create tables

---

## ✅ Frontend Implementado

### Pages
- ✅ **Login Page** (`/login`)
  - Form com validação
  - Error handling
  - Loading states
  - Link para Register

- ✅ **Register Page** (`/register`)
  - Full name, email, username, password
  - Password confirmation
  - Validações client-side
  - Link para Login

### Services
- ✅ **authService** com axios
  - register()
  - login()
  - refreshToken()
  - getCurrentUser()
  - logout()
  - Token management (localStorage)

### Components
- ✅ **ProtectedRoute** wrapper
  - Verifica autenticação
  - Redireciona para login
  - Loading state

---

## 🔧 Configuração Necessária

### 1. Instalar dependências no backend
```bash
cd C:\JarvisAI\server
pip install --upgrade -r requirements.txt
```

### 2. Configurar banco de dados
Adicione ao `.env`:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=jarvis_db

JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 3. Reiniciar backend
```bash
uvicorn api.main:app --reload
```

---

## 📝 Fluxo de Autenticação

### Registro
1. User preenche form em `/register`
2. Frontend valida (senha, email, etc)
3. `POST /auth/register` com dados
4. Backend cria user com password hash
5. Retorna access_token + refresh_token
6. Frontend salva tokens em localStorage
7. Redireciona para `/` (chat)

### Login
1. User preenche form em `/login`
2. `POST /auth/login` com username + password
3. Backend valida credenciais
4. Retorna tokens
5. Frontend salva tokens
6. Redireciona para `/`

### Refresh Token
1. Token expirado em request
2. Interceptor detecta 401
3. `POST /auth/refresh` com refresh_token
4. Recebe novo access_token
5. Retry original request

---

## 🧪 Teste

### 1. Criar conta
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

### 3. Pegar usuário atual
```bash
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Arquivos Criados

### Backend
```
app/
├── models/
│   └── user.py (User model)
├── security/
│   └── auth.py (JWT + password)
├── schemas/
│   └── user.py (Pydantic schemas)
└── database/
    └── db.py (SQLAlchemy setup)

api/routes/
└── auth.py (Auth endpoints)
```

### Frontend
```
src/
├── app/
│   ├── login/page.tsx
│   └── register/page.tsx
├── components/
│   └── ProtectedRoute.tsx
└── lib/
    └── auth.ts (Auth service)
```

---

## 🔒 Segurança

✅ **Password Hashing:**
- Bcrypt com salt
- Senhas nunca em plain text

✅ **JWT Tokens:**
- HS256 algorithm
- 24h expiration (access)
- 7d expiration (refresh)
- Payload: sub, user_id, is_admin, type, exp

✅ **Token Storage:**
- localStorage no cliente
- Sent in Authorization header
- Automatic refresh on 401

✅ **Protected Routes:**
- ProtectedRoute component
- Verifica auth antes render
- Redireciona se não autenticado

---

## ⚠️ TODO - Próximos Passos

- [ ] Atualizar página `/` para usar ProtectedRoute
- [ ] Testar fluxo completo (register → login → chat)
- [ ] Adicionar logout button
- [ ] User profile page
- [ ] Forgot password flow
- [ ] Email verification

---

## 📞 Troubleshooting

### Erro: "PostgreSQL not running"
```bash
# Iniciar PostgreSQL (se não está rodando)
# Windows: Services > PostgreSQL > Start
# Linux: sudo systemctl start postgresql
```

### Erro: "Invalid token"
```bash
# Checar JWT_SECRET_KEY no .env
# Deve ser igual em backend e (não precisa no frontend)
```

### Token não salva em localStorage
```javascript
// Verificar no DevTools Console:
localStorage.getItem('access_token')
```

---

## 🎯 Próximo Sprint

**Sprint 5 - Admin Dashboard**
- Dashboard com estatísticas
- Gerenciar usuários
- Gerenciar documentos
- Ver logs do sistema

---

**Status:** ✅ **PRONTO PARA TESTAR**

Próxima ação: Testar fluxo de registro/login
