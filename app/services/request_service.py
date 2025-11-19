from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import RequestCreate, RequestInDB
from app.database import SessionLocal, RequestDB
import logging

logger = logging.getLogger(__name__)


class RequestService:
    """Service for managing update requests (SQLite storage)"""

    def __init__(self):
        """Initialize request service"""
        logger.info("Using SQLite database for requests storage")

    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()

    def _db_to_pydantic(self, db_request: RequestDB) -> RequestInDB:
        """Convert database model to Pydantic model"""
        return RequestInDB(
            id=db_request.id,
            ngay_tao=db_request.ngay_tao,
            bien_so=db_request.bien_so,
            loai_mau=db_request.loai_mau,
            loai_xe=db_request.loai_xe,
            chu_xe=db_request.chu_xe,
            dia_chi_chu_xe=db_request.dia_chi_chu_xe,
            so_dien_thoai_chu_xe=db_request.so_dien_thoai_chu_xe,
            ma_so_thue_chu_xe=db_request.ma_so_thue_chu_xe,
            ten_nguoi_mua=db_request.ten_nguoi_mua,
            dia_chi_nguoi_mua=db_request.dia_chi_nguoi_mua,
            so_cccd_nguoi_mua=db_request.so_cccd_nguoi_mua,
            so_dien_thoai_nguoi_mua=db_request.so_dien_thoai_nguoi_mua,
            so_khung=db_request.so_khung,
            so_may=db_request.so_may,
            tinh_trang_xe=db_request.tinh_trang_xe,
            ghi_chu=db_request.ghi_chu,
            trang_thai=db_request.trang_thai,
            nguoi_duyet=db_request.nguoi_duyet,
            ngay_duyet=db_request.ngay_duyet,
            ly_do_tu_choi=db_request.ly_do_tu_choi
        )

    def create_request(self, request: RequestCreate) -> RequestInDB:
        """
        Create a new update request

        Args:
            request: Request data

        Returns:
            Created request with ID and timestamp
        """
        db = self._get_db()
        try:
            # Generate unique ID
            request_id = self._generate_request_id(db)

            # Create database record
            db_request = RequestDB(
                id=request_id,
                ngay_tao=datetime.now(),
                trang_thai="pending",
                bien_so=request.bien_so,
                loai_mau=request.loai_mau,
                loai_xe=request.loai_xe,
                chu_xe=request.chu_xe,
                dia_chi_chu_xe=request.dia_chi_chu_xe,
                so_dien_thoai_chu_xe=request.so_dien_thoai_chu_xe,
                ma_so_thue_chu_xe=request.ma_so_thue_chu_xe,
                ten_nguoi_mua=request.ten_nguoi_mua,
                dia_chi_nguoi_mua=request.dia_chi_nguoi_mua,
                so_cccd_nguoi_mua=request.so_cccd_nguoi_mua,
                so_dien_thoai_nguoi_mua=request.so_dien_thoai_nguoi_mua,
                so_khung=request.so_khung,
                so_may=request.so_may,
                tinh_trang_xe=request.tinh_trang_xe,
                ghi_chu=request.ghi_chu
            )

            db.add(db_request)
            db.commit()
            db.refresh(db_request)

            logger.info(f"Created request {request_id} for vehicle {request.bien_so}")
            return self._db_to_pydantic(db_request)

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating request: {e}")
            raise
        finally:
            db.close()

    def _generate_request_id(self, db: Session) -> str:
        """Generate unique request ID"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")

        # Count requests today
        from sqlalchemy import func, extract
        today_count = db.query(func.count(RequestDB.id)).filter(
            func.date(RequestDB.ngay_tao) == now.date()
        ).scalar()

        sequence = today_count + 1
        return f"REQ_{date_str}_{sequence:04d}"

    def get_all_requests(self, loai_mau: Optional[int] = None) -> List[RequestInDB]:
        """
        Get all requests, optionally filtered by form type

        Args:
            loai_mau: Form type (1-10) to filter by

        Returns:
            List of requests
        """
        db = self._get_db()
        try:
            query = db.query(RequestDB).order_by(RequestDB.ngay_tao.desc())

            if loai_mau is not None:
                query = query.filter(RequestDB.loai_mau == loai_mau)

            db_requests = query.all()
            return [self._db_to_pydantic(req) for req in db_requests]

        finally:
            db.close()

    def get_request_by_id(self, request_id: str) -> Optional[RequestInDB]:
        """Get a specific request by ID"""
        db = self._get_db()
        try:
            db_request = db.query(RequestDB).filter(RequestDB.id == request_id).first()
            if db_request:
                return self._db_to_pydantic(db_request)
            return None

        finally:
            db.close()

    def get_statistics(self):
        """Get statistics about requests"""
        db = self._get_db()
        try:
            from sqlalchemy import func

            total = db.query(func.count(RequestDB.id)).scalar()

            by_form = {}
            for i in range(1, 11):
                count = db.query(func.count(RequestDB.id)).filter(RequestDB.loai_mau == i).scalar()
                by_form[f"mau_{i}"] = count

            pending = db.query(func.count(RequestDB.id)).filter(RequestDB.trang_thai == "pending").scalar()
            approved = db.query(func.count(RequestDB.id)).filter(RequestDB.trang_thai == "approved").scalar()
            rejected = db.query(func.count(RequestDB.id)).filter(RequestDB.trang_thai == "rejected").scalar()
            processed = db.query(func.count(RequestDB.id)).filter(RequestDB.trang_thai == "processed").scalar()

            return {
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "processed": processed,
                "by_form": by_form
            }

        finally:
            db.close()

    def update_request_status(self, request_id: str, status: str) -> bool:
        """Update request status"""
        db = self._get_db()
        try:
            db_request = db.query(RequestDB).filter(RequestDB.id == request_id).first()
            if db_request:
                db_request.trang_thai = status
                db.commit()
                return True
            return False

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating request status: {e}")
            return False
        finally:
            db.close()

    def approve_request(self, request_id: str, admin_username: str) -> bool:
        """
        Approve a request

        Args:
            request_id: ID of the request
            admin_username: Username of admin who approved

        Returns:
            True if successful, False otherwise
        """
        db = self._get_db()
        try:
            db_request = db.query(RequestDB).filter(RequestDB.id == request_id).first()

            if not db_request:
                logger.warning(f"Request {request_id} not found")
                return False

            if db_request.trang_thai != "pending":
                logger.warning(f"Request {request_id} is not pending (status: {db_request.trang_thai})")
                return False

            db_request.trang_thai = "approved"
            db_request.nguoi_duyet = admin_username
            db_request.ngay_duyet = datetime.now()
            db.commit()

            logger.info(f"Request {request_id} approved by {admin_username}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error approving request: {e}")
            return False
        finally:
            db.close()

    def reject_request(self, request_id: str, admin_username: str, reason: str = "") -> bool:
        """
        Reject a request

        Args:
            request_id: ID of the request
            admin_username: Username of admin who rejected
            reason: Reason for rejection

        Returns:
            True if successful, False otherwise
        """
        db = self._get_db()
        try:
            db_request = db.query(RequestDB).filter(RequestDB.id == request_id).first()

            if not db_request:
                logger.warning(f"Request {request_id} not found")
                return False

            if db_request.trang_thai != "pending":
                logger.warning(f"Request {request_id} is not pending (status: {db_request.trang_thai})")
                return False

            db_request.trang_thai = "rejected"
            db_request.nguoi_duyet = admin_username
            db_request.ngay_duyet = datetime.now()
            db_request.ly_do_tu_choi = reason
            db.commit()

            logger.info(f"Request {request_id} rejected by {admin_username}. Reason: {reason}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error rejecting request: {e}")
            return False
        finally:
            db.close()

    def mark_as_processed(self, request_id: str) -> bool:
        """
        Mark request as processed (after sending to government)

        Args:
            request_id: ID of the request

        Returns:
            True if successful, False otherwise
        """
        db = self._get_db()
        try:
            db_request = db.query(RequestDB).filter(RequestDB.id == request_id).first()

            if not db_request:
                logger.warning(f"Request {request_id} not found")
                return False

            if db_request.trang_thai != "approved":
                logger.warning(f"Request {request_id} is not approved (status: {db_request.trang_thai})")
                return False

            db_request.trang_thai = "processed"
            db.commit()

            logger.info(f"Request {request_id} marked as processed")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error marking request as processed: {e}")
            return False
        finally:
            db.close()


# Singleton instance
request_service = RequestService()
