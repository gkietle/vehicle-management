from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine with dynamic configuration
# SQLite needs check_same_thread=False, PostgreSQL doesn't
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False  # Set to True to see SQL queries
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class RequestDB(Base):
    """SQLAlchemy model for requests"""
    __tablename__ = "requests"

    id = Column(String, primary_key=True, index=True)
    ngay_tao = Column(DateTime, nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), index=True)  # Link to batch

    # Vehicle info
    bien_so = Column(String, nullable=False, index=True)
    loai_mau = Column(Integer, nullable=False)
    loai_xe = Column(String)
    mau_bien = Column(String)

    # Owner info
    chu_xe = Column(String)
    dia_chi_chu_xe = Column(Text)
    so_dien_thoai_chu_xe = Column(String)
    ma_so_thue_chu_xe = Column(String)

    # GPLX and CCCD info for owner
    ngay_cap_cccd_chu_xe = Column(String)
    so_gplx_chu_xe = Column(String)
    ngay_cap_gplx_chu_xe = Column(String)
    co_quan_cap_gplx_chu_xe = Column(String)

    # Buyer info (for transfer forms 2, 3, 4, 7, 8, 9)
    ten_nguoi_mua = Column(String)
    dia_chi_nguoi_mua = Column(Text)
    so_cccd_nguoi_mua = Column(String)
    ngay_cap_cccd_nguoi_mua = Column(String)
    so_dien_thoai_nguoi_mua = Column(String)
    ban_sao_chuyen_nhuong = Column(String)

    # Vehicle identification
    so_khung = Column(String)
    so_may = Column(String)

    # For form 10 specifically (seller and current user info)
    ten_nguoi_dang_su_dung = Column(String)
    dia_chi_nguoi_dang_su_dung = Column(Text)
    ten_nguoi_ban = Column(String)
    dia_chi_nguoi_ban = Column(Text)
    so_dien_thoai_nguoi_ban = Column(String)
    so_cccd_nguoi_ban = Column(String)
    ngay_cap_cccd_nguoi_ban = Column(String)

    # Additional info
    tinh_trang_xe = Column(String)
    ghi_chu = Column(Text)

    # Status and approval
    trang_thai = Column(String, default="pending", index=True)  # pending, approved, rejected, processed
    nguoi_duyet = Column(String)  # Admin username who approved/rejected
    ngay_duyet = Column(DateTime)  # Date of approval/rejection
    ly_do_tu_choi = Column(Text)  # Rejection reason

    # Relationship
    batch = relationship("BatchDB", back_populates="requests")


class BatchDB(Base):
    """SQLAlchemy model for data batches"""
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # e.g., "Tháng 10/2024"
    description = Column(Text)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False, index=True)  # Only one batch can be active

    # Relationship
    data_files = relationship("DataFileDB", back_populates="batch", cascade="all, delete-orphan")
    requests = relationship("RequestDB", back_populates="batch")


class DataFileDB(Base):
    """SQLAlchemy model for data files in batches"""
    __tablename__ = "data_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)

    # File info
    filename = Column(String, nullable=False)  # Sanitized filename
    original_filename = Column(String, nullable=False)  # Original uploaded filename
    file_path = Column(String, nullable=False, unique=True)  # Absolute path to file
    file_size = Column(BigInteger)  # File size in bytes

    # Metadata
    uploaded_at = Column(DateTime, nullable=False)
    sheet_count = Column(Integer, default=0)  # Number of sheets in Excel file
    record_count = Column(Integer, default=0)  # Total records imported from this file

    # Relationship
    batch = relationship("BatchDB", back_populates="data_files")
    vehicle_records = relationship("VehicleRecordDB", back_populates="data_file", cascade="all, delete-orphan")


class VehicleRecordDB(Base):
    """SQLAlchemy model for vehicle records imported from Excel files"""
    __tablename__ = "vehicle_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_file_id = Column(Integer, ForeignKey("data_files.id"), nullable=False, index=True)

    # Source info
    sheet_name = Column(String)  # Sheet name in Excel file

    # Vehicle data (matching VehicleInfo model)
    bien_so = Column(String, nullable=False, index=True)  # License plate
    mau_bien = Column(String)
    loai_xe = Column(String)
    ten = Column(String, index=True)  # Owner name
    dia_chi_dang_ky_xe = Column(Text)
    khu_pho = Column(String)
    dia_chi_thuong_tru = Column(Text)
    noi_o_hien_tai = Column(Text)
    so_khung = Column(String, index=True)  # Add index for search performance
    so_may = Column(String, index=True)  # Add index for search performance
    so_dien_thoai = Column(String, index=True)  # Add index for search performance
    loai_giay_to = Column(String)
    so_giay_to = Column(String)
    trang_thai_xe = Column(String)
    trang_thai_dang_ky = Column(String)

    # Relationship
    data_file = relationship("DataFileDB", back_populates="vehicle_records")


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
