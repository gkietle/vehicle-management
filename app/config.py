from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """Application settings"""

    # App info
    APP_NAME: str = "Hệ thống Tra cứu & Quản lý Phương tiện"
    APP_VERSION: str = "1.0.0"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMPLATE_DIR: Path = BASE_DIR / "app" / "templates"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"

    # Data files (legacy - for fallback)
    BIEN_XANH_FILE: Path = DATA_DIR / "dulieuphuongtien" / "1.BIEN_XANH_TINH_DONG_NAI 60 LOC MOTO (Long Bình).xlsx"
    BIEN_TRANG_VANG_KHONG_C06_DIR: Path = DATA_DIR / "dulieuphuongtien" / "2. MOTO_BIEN_TRANG_VANG_KHONG_C06_TINH_DONG_NAI"
    BIEN_TRANG_VANG_CO_C06_DIR: Path = DATA_DIR / "dulieuphuongtien" / "3. MOTO_BIEN_TRANG_VANG_CO__C06_TINH_DONG_NAI"

    # Requests storage
    REQUESTS_DIR: Path = BASE_DIR / "requests"

    # Database - supports both SQLite (dev) and PostgreSQL (production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.db'}")

    # Admin credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create requests directory if not exists
settings.REQUESTS_DIR.mkdir(exist_ok=True)
