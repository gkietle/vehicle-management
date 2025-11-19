from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.config import settings
from app.routers import public, admin
from app.services.vehicle_service import vehicle_service
from app.database import init_db
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hệ thống tra cứu và quản lý thông tin phương tiện giao thông"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))

# Include routers
app.include_router(public.router, tags=["Public"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    logger.info("Loading vehicle data...")
    # Load data files from active batch or fallback to legacy
    vehicle_service.reload_data_files()
    stats = vehicle_service.get_statistics()
    logger.info(f"Vehicle data loaded: {stats}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Trang chủ"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = vehicle_service.get_statistics()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "vehicle_stats": stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
