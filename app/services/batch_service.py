from datetime import datetime
from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.config import settings
from app.database import SessionLocal, BatchDB, DataFileDB, VehicleRecordDB
import pandas as pd
import shutil
import logging

logger = logging.getLogger(__name__)


class BatchService:
    """Service for managing data batches"""

    def __init__(self):
        """Initialize batch service"""
        self.batches_dir = settings.DATA_DIR / "batches"
        self.batches_dir.mkdir(exist_ok=True, parents=True)
        logger.info("Batch service initialized")

    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()

    def create_batch(self, name: str, description: str = "") -> BatchDB:
        """
        Create a new data batch

        Args:
            name: Batch name (e.g., "Tháng 10/2024")
            description: Optional description

        Returns:
            Created batch
        """
        db = self._get_db()
        try:
            # Check if batch with same name exists
            existing = db.query(BatchDB).filter(BatchDB.name == name).first()
            if existing:
                raise ValueError(f"Batch with name '{name}' already exists")

            # Create batch
            batch = BatchDB(
                name=name,
                description=description,
                created_at=datetime.now(),
                is_active=False
            )

            db.add(batch)
            db.commit()
            db.refresh(batch)

            # Create directory for this batch
            batch_dir = self.batches_dir / str(batch.id)
            batch_dir.mkdir(exist_ok=True)

            logger.info(f"Created batch: {name} (ID: {batch.id})")
            return batch

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating batch: {e}")
            raise
        finally:
            db.close()

    def get_all_batches(self) -> List[BatchDB]:
        """Get all batches ordered by creation date (newest first)"""
        db = self._get_db()
        try:
            batches = db.query(BatchDB).order_by(desc(BatchDB.created_at)).all()
            return batches
        finally:
            db.close()

    def get_batch_by_id(self, batch_id: int) -> Optional[BatchDB]:
        """Get batch by ID"""
        db = self._get_db()
        try:
            return db.query(BatchDB).filter(BatchDB.id == batch_id).first()
        finally:
            db.close()

    def get_active_batch(self) -> Optional[BatchDB]:
        """Get the currently active batch"""
        db = self._get_db()
        try:
            return db.query(BatchDB).filter(BatchDB.is_active == True).first()
        finally:
            db.close()

    def set_active_batch(self, batch_id: int) -> bool:
        """
        Set a batch as active (and deactivate all others)

        Args:
            batch_id: ID of batch to activate

        Returns:
            True if successful
        """
        db = self._get_db()
        try:
            # Check if batch exists
            batch = db.query(BatchDB).filter(BatchDB.id == batch_id).first()
            if not batch:
                logger.warning(f"Batch {batch_id} not found")
                return False

            # Deactivate all batches
            db.query(BatchDB).update({BatchDB.is_active: False})

            # Activate the selected batch
            batch.is_active = True
            db.commit()

            logger.info(f"Set batch {batch_id} ({batch.name}) as active")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error setting active batch: {e}")
            return False
        finally:
            db.close()

    def upload_file_to_batch(self, batch_id: int, file_content: bytes, filename: str) -> DataFileDB:
        """
        Upload a file to a batch

        Args:
            batch_id: ID of batch to upload to
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Created data file record
        """
        db = self._get_db()
        try:
            # Check if batch exists
            batch = db.query(BatchDB).filter(BatchDB.id == batch_id).first()
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")

            # Create batch directory if not exists
            batch_dir = self.batches_dir / str(batch_id)
            batch_dir.mkdir(exist_ok=True, parents=True)

            # Sanitize filename
            safe_filename = self._sanitize_filename(filename)

            # Create unique filename if file already exists
            file_path = batch_dir / safe_filename
            counter = 1
            while file_path.exists():
                name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
                safe_filename = f"{name}_{counter}.{ext}" if ext else f"{name}_{counter}"
                file_path = batch_dir / safe_filename
                counter += 1

            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Get file info
            file_size = len(file_content)
            sheet_count = self._count_excel_sheets(file_path)

            # Create database record
            data_file = DataFileDB(
                batch_id=batch_id,
                filename=safe_filename,
                original_filename=filename,
                file_path=str(file_path.absolute()),
                file_size=file_size,
                uploaded_at=datetime.now(),
                sheet_count=sheet_count
            )

            db.add(data_file)
            db.commit()
            db.refresh(data_file)

            file_id = data_file.id  # Store the ID before potential detachment

            # Parse and import Excel data into database
            try:
                record_count = self._parse_and_import_excel(file_path, file_id)
                # Re-query the object to attach it to the session
                data_file = db.query(DataFileDB).filter(DataFileDB.id == file_id).first()
                if data_file:
                    data_file.record_count = record_count
                    db.commit()
                    db.refresh(data_file)
                logger.info(f"Imported {record_count} records from {filename}")
            except Exception as e:
                logger.error(f"Error parsing Excel file {filename}: {e}")
                # Don't fail the upload, just log the error
                # Re-query to return a valid object
                data_file = db.query(DataFileDB).filter(DataFileDB.id == file_id).first()

            logger.info(f"Uploaded file {filename} to batch {batch_id} ({file_size} bytes, {sheet_count} sheets)")
            return data_file

        except Exception as e:
            db.rollback()
            # Clean up file if database insert failed
            if 'file_path' in locals() and Path(file_path).exists():
                Path(file_path).unlink()
            logger.error(f"Error uploading file: {e}")
            raise
        finally:
            db.close()

    def get_batch_files(self, batch_id: int) -> List[DataFileDB]:
        """Get all files in a batch"""
        db = self._get_db()
        try:
            files = db.query(DataFileDB).filter(DataFileDB.batch_id == batch_id).order_by(DataFileDB.uploaded_at).all()
            return files
        finally:
            db.close()

    def delete_batch(self, batch_id: int) -> bool:
        """
        Delete a batch and all its files

        Args:
            batch_id: ID of batch to delete

        Returns:
            True if successful
        """
        db = self._get_db()
        try:
            batch = db.query(BatchDB).filter(BatchDB.id == batch_id).first()
            if not batch:
                logger.warning(f"Batch {batch_id} not found")
                return False

            # Don't allow deleting active batch
            if batch.is_active:
                logger.warning(f"Cannot delete active batch {batch_id}")
                return False

            # Delete directory
            batch_dir = self.batches_dir / str(batch_id)
            if batch_dir.exists():
                shutil.rmtree(batch_dir)

            # Delete from database (cascade will delete data_files)
            db.delete(batch)
            db.commit()

            logger.info(f"Deleted batch {batch_id} ({batch.name})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting batch: {e}")
            return False
        finally:
            db.close()

    def delete_file(self, file_id: int) -> bool:
        """
        Delete a file from a batch

        Args:
            file_id: ID of file to delete

        Returns:
            True if successful
        """
        db = self._get_db()
        try:
            data_file = db.query(DataFileDB).filter(DataFileDB.id == file_id).first()
            if not data_file:
                logger.warning(f"File {file_id} not found")
                return False

            # Delete physical file
            file_path = Path(data_file.file_path)
            if file_path.exists():
                file_path.unlink()

            # Delete from database
            db.delete(data_file)
            db.commit()

            logger.info(f"Deleted file {file_id} ({data_file.original_filename})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting file: {e}")
            return False
        finally:
            db.close()

    def get_active_batch_files(self) -> List[Path]:
        """
        Get list of file paths from the active batch

        Returns:
            List of Path objects for files in active batch
        """
        db = self._get_db()
        try:
            active_batch = db.query(BatchDB).filter(BatchDB.is_active == True).first()
            if not active_batch:
                logger.warning("No active batch found")
                return []

            files = db.query(DataFileDB).filter(DataFileDB.batch_id == active_batch.id).all()
            return [Path(f.file_path) for f in files]

        finally:
            db.close()

    def get_batch_records(self, batch_id: int, search: Optional[str] = None, limit: int = 100, offset: int = 0):
        """
        Get vehicle records from a batch with optional search

        Args:
            batch_id: ID of batch
            search: Search term (bien_so, ten, etc.)
            limit: Max records to return
            offset: Pagination offset

        Returns:
            List of records with source file info
        """
        db = self._get_db()
        try:
            # Query records directly with batch filter (optimized)
            query = db.query(VehicleRecordDB, DataFileDB).join(
                DataFileDB, VehicleRecordDB.data_file_id == DataFileDB.id
            ).filter(
                DataFileDB.batch_id == batch_id
            )

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        VehicleRecordDB.bien_so.like(search_term),
                        VehicleRecordDB.ten.like(search_term),
                        VehicleRecordDB.so_khung.like(search_term),
                        VehicleRecordDB.so_may.like(search_term),
                        VehicleRecordDB.so_dien_thoai.like(search_term)
                    )
                )

            # Get total count
            total = query.count()

            # Get paginated results
            results = query.order_by(VehicleRecordDB.id.desc()).limit(limit).offset(offset).all()

            records = []
            for vehicle_record, data_file in results:
                records.append({
                    "id": vehicle_record.id,
                    "bien_so": vehicle_record.bien_so,
                    "loai_xe": vehicle_record.loai_xe,
                    "ten": vehicle_record.ten,
                    "dia_chi_dang_ky_xe": vehicle_record.dia_chi_dang_ky_xe,
                    "khu_pho": vehicle_record.khu_pho,
                    "so_khung": vehicle_record.so_khung,
                    "so_may": vehicle_record.so_may,
                    "so_dien_thoai": vehicle_record.so_dien_thoai,
                    "trang_thai_xe": vehicle_record.trang_thai_xe,
                    "sheet_name": vehicle_record.sheet_name,
                    # Source file info
                    "source_file": data_file.original_filename,
                    "source_file_id": data_file.id,
                })

            return records, total

        finally:
            db.close()

    def _parse_and_import_excel(self, file_path: Path, data_file_id: int) -> int:
        """
        Parse Excel file and import all records into database

        Args:
            file_path: Path to Excel file
            data_file_id: ID of DataFileDB record

        Returns:
            Number of records imported
        """
        db = self._get_db()
        total_imported = 0

        try:
            # Read Excel file
            xls = pd.ExcelFile(file_path)
            logger.info(f"Processing file {file_path.name} with {len(xls.sheet_names)} sheets: {xls.sheet_names}")

            # Process each sheet
            for sheet_name in xls.sheet_names:
                # Only process sheet named '26'
                if '26' not in sheet_name:
                    logger.info(f"Skipping sheet '{sheet_name}' (only importing sheet '26')")
                    continue

                sheet_imported = 0
                logger.info(f"Processing sheet '{sheet_name}'...")

                df = pd.read_excel(file_path, sheet_name=sheet_name)
                logger.info(f"Sheet '{sheet_name}' has {len(df)} rows and columns: {df.columns.tolist()}")

                # Skip if no BIEN_SO column
                if 'BIEN_SO' not in df.columns:
                    logger.warning(f"Sheet '{sheet_name}' has no BIEN_SO column, skipping")
                    continue

                # Import records from this sheet
                for _, row in df.iterrows():
                    # Skip rows without bien_so
                    if pd.isna(row.get('BIEN_SO')) or str(row.get('BIEN_SO')).strip() == '':
                        continue

                    record = VehicleRecordDB(
                        data_file_id=data_file_id,
                        sheet_name=sheet_name,
                        bien_so=str(row.get('BIEN_SO', '')).strip(),
                        mau_bien=self._safe_str(row.get('MAU_BIEN')),
                        loai_xe=self._safe_str(row.get('LOAI_XE')),
                        ten=self._safe_str(row.get('TEN')),
                        dia_chi_dang_ky_xe=self._safe_str(row.get('DIA_CHI_DANG_KY_XE')),
                        khu_pho=self._safe_str(row.get('Khu Phố')),
                        dia_chi_thuong_tru=self._safe_str(row.get('DIA_CHI_THUONG_TRU')),
                        noi_o_hien_tai=self._safe_str(row.get('NOI_O_HIEN_TAI')),
                        so_khung=self._safe_str(row.get('SO_KHUNG')),
                        so_may=self._safe_str(row.get('SO_MAY')),
                        so_dien_thoai=self._safe_str(row.get('SO_DIEN_THOAI')),
                        loai_giay_to=self._safe_str(row.get('LOAI_GIAY_TO')),
                        so_giay_to=self._safe_str(row.get('SO_GIAY_TO')),
                        trang_thai_xe=self._safe_str(row.get('TRANG_THAI_XE')),
                        trang_thai_dang_ky=self._safe_str(row.get('TRANG_THAI_DANG_KY'))
                    )

                    db.add(record)
                    sheet_imported += 1
                    total_imported += 1

                logger.info(f"Sheet '{sheet_name}': imported {sheet_imported} records (total so far: {total_imported})")

            db.commit()
            logger.info(f"COMPLETED: Total imported {total_imported} records from {file_path.name}")
            return total_imported

        except Exception as e:
            db.rollback()
            logger.error(f"Error importing Excel data: {e}")
            raise
        finally:
            db.close()

    def _safe_str(self, value) -> str:
        """Safely convert value to string, handling NaN"""
        if pd.isna(value):
            return ""
        return str(value).strip()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove unsafe characters"""
        # Remove path separators and keep only alphanumeric, spaces, dots, dashes, underscores
        import re
        safe_name = re.sub(r'[^\w\s\.\-]', '_', filename)
        return safe_name

    def _count_excel_sheets(self, file_path: Path) -> int:
        """Count number of sheets in Excel file"""
        try:
            xls = pd.ExcelFile(file_path)
            return len(xls.sheet_names)
        except Exception as e:
            logger.error(f"Error counting sheets in {file_path}: {e}")
            return 0


# Singleton instance
batch_service = BatchService()
