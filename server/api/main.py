"""
Ivy AI - Intelligent Versatile Assistant
Main FastAPI application
Enhanced from Jarvis AI with modular agent architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.health import router as health_router
from api.routes.system import router as system_router
from api.routes.documents import router as documents_router
from api.routes.chat import router as chat_router
from api.routes.auth import router as auth_router
from api.routes.admin import router as admin_router
from api.routes.n8n import router as n8n_router
from api.routes.agents import router as agents_router
from api.routes.tools import router as tools_router
from api.routes.integration import router as integration_router
from api.routes.vision import router as vision_router
from api.routes.audio import router as audio_router
from api.routes.plugins import router as plugins_router
from api.routes.admin_dashboard import router as admin_dashboard_router
from app.utils.logger import setup_logger
from config.settings import get_settings
from app.database.db import init_db
from app.agents.init import initialize_agents
from app.tools.init import initialize_tools
from app.plugins.init import initialize_plugins

logger = setup_logger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced AI-powered RAG system integrated with n8n",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    init_db()
except Exception as e:
    logger.warning(f"Database initialization warning: {str(e)}")

# Initialize agents
try:
    initialize_agents()
except Exception as e:
    logger.error(f"Agent initialization failed: {str(e)}")

# Initialize tools
try:
    initialize_tools()
except Exception as e:
    logger.error(f"Tool initialization failed: {str(e)}")

# Initialize plugins
try:
    initialize_plugins()
except Exception as e:
    logger.error(f"Plugin initialization failed: {str(e)}")

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(n8n_router)
app.include_router(system_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(agents_router)
app.include_router(tools_router)
app.include_router(integration_router)
app.include_router(vision_router)
app.include_router(audio_router)
app.include_router(plugins_router)
app.include_router(admin_dashboard_router)

logger.info(f"Jarvis AI application initialized: {settings.APP_NAME} v{settings.APP_VERSION}")