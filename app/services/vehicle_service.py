import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from app.config import settings
from app.models import VehicleInfo
import logging

logger = logging.getLogger(__name__)


class VehicleService:
    """Service for searching and managing vehicle data (Batch-based)"""

    def __init__(self):
        """Initialize vehicle service"""
        self.data_files = []
        self.use_batch_system = True
        logger.info("Vehicle service initialized (batch-based)")

    def reload_data_files(self):
        """Reload data files from active batch or fallback to legacy"""
        from app.services.batch_service import batch_service

        if self.use_batch_system:
            # Get files from active batch
            batch_files = batch_service.get_active_batch_files()

            if batch_files:
                self.data_files = batch_files
                logger.info(f"Loaded {len(self.data_files)} files from active batch")
                return

            logger.warning("No active batch found, falling back to legacy data")

        # Fallback to legacy data directories
        self._initialize_legacy_files()

    def _initialize_legacy_files(self):
        """Build list of Excel files from legacy directories (fallback)"""
        self.data_files = []

        # Add Biển Xanh file
        if settings.BIEN_XANH_FILE.exists():
            self.data_files.append(settings.BIEN_XANH_FILE)

        # Add Biển Trắng Vàng files
        directories = [
            settings.BIEN_TRANG_VANG_KHONG_C06_DIR,
            settings.BIEN_TRANG_VANG_CO_C06_DIR
        ]

        for directory in directories:
            if not directory.exists():
                continue

            excel_files = list(directory.glob("*.xlsx"))
            for file_path in excel_files:
                if not (file_path.name.startswith('.') or file_path.name.startswith('~')):
                    self.data_files.append(file_path)

        logger.info(f"Initialized legacy files: {len(self.data_files)} data files")

    def search_by_bien_so(self, bien_so: str) -> Optional[VehicleInfo]:
        """
        Search for vehicle by license plate number (database only)

        Args:
            bien_so: License plate number (e.g., "60B100129")

        Returns:
            VehicleInfo if found, None otherwise
        """
        # Clean and normalize bien_so
        bien_so = bien_so.strip().upper()
        logger.info(f"Searching for: {bien_so}")

        # Search in database only (fast)
        return self._search_in_database(bien_so)

    def search_by_cccd(self, cccd: str) -> Optional[List[VehicleInfo]]:
        """
        Search for vehicles by CCCD (Citizen ID) number

        Args:
            cccd: CCCD number (e.g., "001234567890")

        Returns:
            List of VehicleInfo if found, None otherwise
        """
        # Clean and normalize cccd
        cccd = cccd.strip()
        logger.info(f"Searching for vehicles with CCCD: {cccd}")

        # Search in database only (fast)
        return self._search_in_database_by_cccd(cccd)

    def _search_in_database(self, bien_so: str) -> Optional[VehicleInfo]:
        """Search for vehicle in database (fastest method)"""
        from app.database import SessionLocal, VehicleRecordDB, DataFileDB, BatchDB

        db = SessionLocal()
        try:
            # Search for vehicle in active batch
            record = db.query(VehicleRecordDB).join(
                DataFileDB, VehicleRecordDB.data_file_id == DataFileDB.id
            ).join(
                BatchDB, DataFileDB.batch_id == BatchDB.id
            ).filter(
                BatchDB.is_active == True,
                VehicleRecordDB.bien_so == bien_so
            ).first()

            if record:
                logger.info(f"Found vehicle {bien_so} in database")
                return VehicleInfo(
                    bien_so=record.bien_so or "",
                    mau_bien=record.mau_bien or "",
                    loai_xe=record.loai_xe or "",
                    ten=record.ten or "",
                    dia_chi_dang_ky_xe=record.dia_chi_dang_ky_xe or "",
                    khu_pho=record.khu_pho or "",
                    dia_chi_thuong_tru=record.dia_chi_thuong_tru or "",
                    noi_o_hien_tai=record.noi_o_hien_tai or "",
                    so_khung=record.so_khung or "",
                    so_may=record.so_may or "",
                    so_dien_thoai=record.so_dien_thoai or "",
                    loai_giay_to=record.loai_giay_to or "",
                    so_giay_to=record.so_giay_to or "",
                    trang_thai_xe=record.trang_thai_xe or "",
                    trang_thai_dang_ky=record.trang_thai_dang_ky or ""
                )

            logger.info(f"Vehicle {bien_so} not found in database")
            return None

        except Exception as e:
            logger.error(f"Error searching in database: {e}")
            return None
        finally:
            db.close()

    def _search_in_database_by_cccd(self, cccd: str) -> Optional[List[VehicleInfo]]:
        """Search for vehicles by CCCD in database"""
        from app.database import SessionLocal, VehicleRecordDB, DataFileDB, BatchDB

        db = SessionLocal()
        try:
            # Search for vehicles in active batch with matching CCCD
            records = db.query(VehicleRecordDB).join(
                DataFileDB, VehicleRecordDB.data_file_id == DataFileDB.id
            ).join(
                BatchDB, DataFileDB.batch_id == BatchDB.id
            ).filter(
                BatchDB.is_active == True,
                VehicleRecordDB.so_giay_to == cccd
            ).all()

            if records:
                logger.info(f"Found {len(records)} vehicle(s) with CCCD {cccd} in database")
                vehicles = []
                for record in records:
                    vehicles.append(VehicleInfo(
                        bien_so=record.bien_so or "",
                        mau_bien=record.mau_bien or "",
                        loai_xe=record.loai_xe or "",
                        ten=record.ten or "",
                        dia_chi_dang_ky_xe=record.dia_chi_dang_ky_xe or "",
                        khu_pho=record.khu_pho or "",
                        dia_chi_thuong_tru=record.dia_chi_thuong_tru or "",
                        noi_o_hien_tai=record.noi_o_hien_tai or "",
                        so_khung=record.so_khung or "",
                        so_may=record.so_may or "",
                        so_dien_thoai=record.so_dien_thoai or "",
                        loai_giay_to=record.loai_giay_to or "",
                        so_giay_to=record.so_giay_to or "",
                        trang_thai_xe=record.trang_thai_xe or "",
                        trang_thai_dang_ky=record.trang_thai_dang_ky or ""
                    ))
                return vehicles

            logger.info(f"No vehicles found with CCCD {cccd} in database")
            return None

        except Exception as e:
            logger.error(f"Error searching by CCCD in database: {e}")
            return None
        finally:
            db.close()

    def _search_in_local_files(self, bien_so: str) -> Optional[VehicleInfo]:
        """Search for vehicle in local Excel files"""
        # Search in each file
        for file_path in self.data_files:
            result = self._search_in_file(file_path, bien_so)
            if result:
                logger.info(f"Found vehicle {bien_so} in {file_path.name}")
                return result

        logger.info(f"Vehicle {bien_so} not found in any data file")
        return None

    def _search_in_file(self, file_path: Path, bien_so: str) -> Optional[VehicleInfo]:
        """Search for vehicle in a specific Excel file (lazy loading)"""
        try:
            # Read Excel file
            xls = pd.ExcelFile(file_path)

            # Search in each sheet
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Search for bien_so
                if 'BIEN_SO' in df.columns:
                    mask = df['BIEN_SO'].astype(str).str.upper() == bien_so
                    matches = df[mask]

                    if len(matches) > 0:
                        return self._row_to_vehicle_info(matches.iloc[0])

        except Exception as e:
            logger.error(f"Error searching in {file_path.name}: {e}")

        return None

    def _search_in_dataframe(self, df: pd.DataFrame, bien_so: str) -> Optional[VehicleInfo]:
        """Search for vehicle in a specific dataframe"""
        try:
            # Find matching row
            mask = df['BIEN_SO'].astype(str).str.upper() == bien_so
            matches = df[mask]

            if len(matches) == 0:
                return None

            # Get first match
            row = matches.iloc[0]

            # Convert to VehicleInfo
            return self._row_to_vehicle_info(row)

        except Exception as e:
            logger.error(f"Error searching in dataframe: {e}")
            return None

    def _row_to_vehicle_info(self, row: pd.Series) -> VehicleInfo:
        """Convert DataFrame row to VehicleInfo model"""

        def safe_get(key: str, default: str = "") -> str:
            """Safely get value from row, handling NaN"""
            value = row.get(key, default)
            if pd.isna(value):
                return default
            return str(value)

        return VehicleInfo(
            bien_so=safe_get('BIEN_SO'),
            mau_bien=safe_get('MAU_BIEN'),
            loai_xe=safe_get('LOAI_XE'),
            ten=safe_get('TEN'),
            dia_chi_dang_ky_xe=safe_get('DIA_CHI_DANG_KY_XE'),
            khu_pho=safe_get('Khu Phố'),
            dia_chi_thuong_tru=safe_get('DIA_CHI_THUONG_TRU'),
            noi_o_hien_tai=safe_get('NOI_O_HIEN_TAI'),
            so_khung=safe_get('SO_KHUNG'),
            so_may=safe_get('SO_MAY'),
            so_dien_thoai=safe_get('SO_DIEN_THOAI'),
            loai_giay_to=safe_get('LOAI_GIAY_TO'),
            so_giay_to=safe_get('SO_GIAY_TO'),
            trang_thai_xe=safe_get('TRANG_THAI_XE'),
            trang_thai_dang_ky=safe_get('TRANG_THAI_DANG_KY')
        )

    def get_statistics(self) -> Dict:
        """Get statistics about vehicle data files"""
        return {
            "total_vehicles": "Chưa thống kê (Lazy Loading)",
            "data_files": len(self.data_files),
            "bien_xanh_files": 1 if settings.BIEN_XANH_FILE.exists() else 0,
            "bien_trang_vang_files": len(self.data_files) - (1 if settings.BIEN_XANH_FILE.exists() else 0)
        }


# Singleton instance
vehicle_service = VehicleService()
