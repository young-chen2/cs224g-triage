from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as main_router
from src.api.auth_routes import router as auth_router
from src.api.provider_endpoints import router as provider_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Healthcare Triage API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "cs224g-triage.vercel.app", "http://localhost:3000"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(main_router)
app.include_router(auth_router)
app.include_router(provider_router)

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}