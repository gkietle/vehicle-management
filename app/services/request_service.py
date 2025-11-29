from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import RequestCreate, RequestInDB
from app.database import SessionLocal, RequestDB, BatchDB
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
        # Get batch name if batch relationship is loaded
        batch_name = None
        if db_request.batch:
            batch_name = db_request.batch.name

        return RequestInDB(
            id=db_request.id,
            ngay_tao=db_request.ngay_tao,
            batch_id=db_request.batch_id,
            batch_name=batch_name,
            bien_so=db_request.bien_so,
            loai_mau=db_request.loai_mau,
            loai_xe=db_request.loai_xe,
            mau_bien=db_request.mau_bien,
            chu_xe=db_request.chu_xe,
            dia_chi_chu_xe=db_request.dia_chi_chu_xe,
            so_dien_thoai_chu_xe=db_request.so_dien_thoai_chu_xe,
            ma_so_thue_chu_xe=db_request.ma_so_thue_chu_xe,
            ngay_cap_cccd_chu_xe=db_request.ngay_cap_cccd_chu_xe,
            so_gplx_chu_xe=db_request.so_gplx_chu_xe,
            ngay_cap_gplx_chu_xe=db_request.ngay_cap_gplx_chu_xe,
            co_quan_cap_gplx_chu_xe=db_request.co_quan_cap_gplx_chu_xe,
            ten_nguoi_mua=db_request.ten_nguoi_mua,
            dia_chi_nguoi_mua=db_request.dia_chi_nguoi_mua,
            so_cccd_nguoi_mua=db_request.so_cccd_nguoi_mua,
            ngay_cap_cccd_nguoi_mua=db_request.ngay_cap_cccd_nguoi_mua,
            so_dien_thoai_nguoi_mua=db_request.so_dien_thoai_nguoi_mua,
            ban_sao_chuyen_nhuong=db_request.ban_sao_chuyen_nhuong,
            so_khung=db_request.so_khung,
            so_may=db_request.so_may,
            ten_nguoi_dang_su_dung=db_request.ten_nguoi_dang_su_dung,
            dia_chi_nguoi_dang_su_dung=db_request.dia_chi_nguoi_dang_su_dung,
            ten_nguoi_ban=db_request.ten_nguoi_ban,
            dia_chi_nguoi_ban=db_request.dia_chi_nguoi_ban,
            so_dien_thoai_nguoi_ban=db_request.so_dien_thoai_nguoi_ban,
            so_cccd_nguoi_ban=db_request.so_cccd_nguoi_ban,
            ngay_cap_cccd_nguoi_ban=db_request.ngay_cap_cccd_nguoi_ban,
            tinh_trang_xe=db_request.tinh_trang_xe,
            ghi_chu=db_request.ghi_chu,
            trang_thai=db_request.trang_thai,
            version=db_request.version if hasattr(db_request, 'version') else 1,
            is_latest_approved=db_request.is_latest_approved if hasattr(db_request, 'is_latest_approved') else False,
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

            # Get active batch
            active_batch = db.query(BatchDB).filter(BatchDB.is_active == True).first()
            batch_id = active_batch.id if active_batch else None

            if not batch_id:
                logger.warning("No active batch found, creating request without batch")

            # Calculate version number for this bien_so + loai_mau
            from sqlalchemy import func
            max_version = db.query(func.max(RequestDB.version)).filter(
                RequestDB.bien_so == request.bien_so,
                RequestDB.loai_mau == request.loai_mau
            ).scalar()
            version = (max_version or 0) + 1

            logger.info(f"Creating request version {version} for {request.bien_so} mẫu {request.loai_mau}")

            # Create database record
            db_request = RequestDB(
                id=request_id,
                ngay_tao=datetime.now(),
                trang_thai="pending",
                version=version,
                is_latest_approved=False,
                batch_id=batch_id,
                bien_so=request.bien_so,
                loai_mau=request.loai_mau,
                loai_xe=request.loai_xe,
                mau_bien=request.mau_bien,
                chu_xe=request.chu_xe,
                dia_chi_chu_xe=request.dia_chi_chu_xe,
                so_dien_thoai_chu_xe=request.so_dien_thoai_chu_xe,
                ma_so_thue_chu_xe=request.ma_so_thue_chu_xe,
                ngay_cap_cccd_chu_xe=request.ngay_cap_cccd_chu_xe,
                so_gplx_chu_xe=request.so_gplx_chu_xe,
                ngay_cap_gplx_chu_xe=request.ngay_cap_gplx_chu_xe,
                co_quan_cap_gplx_chu_xe=request.co_quan_cap_gplx_chu_xe,
                ten_nguoi_mua=request.ten_nguoi_mua,
                dia_chi_nguoi_mua=request.dia_chi_nguoi_mua,
                so_cccd_nguoi_mua=request.so_cccd_nguoi_mua,
                ngay_cap_cccd_nguoi_mua=request.ngay_cap_cccd_nguoi_mua,
                so_dien_thoai_nguoi_mua=request.so_dien_thoai_nguoi_mua,
                ban_sao_chuyen_nhuong=request.ban_sao_chuyen_nhuong,
                so_khung=request.so_khung,
                so_may=request.so_may,
                ten_nguoi_dang_su_dung=request.ten_nguoi_dang_su_dung,
                dia_chi_nguoi_dang_su_dung=request.dia_chi_nguoi_dang_su_dung,
                ten_nguoi_ban=request.ten_nguoi_ban,
                dia_chi_nguoi_ban=request.dia_chi_nguoi_ban,
                so_dien_thoai_nguoi_ban=request.so_dien_thoai_nguoi_ban,
                so_cccd_nguoi_ban=request.so_cccd_nguoi_ban,
                ngay_cap_cccd_nguoi_ban=request.ngay_cap_cccd_nguoi_ban,
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

    def get_all_requests(self, loai_mau: Optional[int] = None, batch_id: Optional[int] = None, latest_approved_only: bool = False) -> List[RequestInDB]:
        """
        Get all requests, optionally filtered by form type and/or batch

        Args:
            loai_mau: Form type (1-10) to filter by
            batch_id: Batch ID to filter by (if None, get all)
            latest_approved_only: If True, only return latest approved version for each bien_so + loai_mau

        Returns:
            List of requests
        """
        db = self._get_db()
        try:
            from sqlalchemy.orm import joinedload

            # Eager load batch relationship
            query = db.query(RequestDB).options(joinedload(RequestDB.batch)).order_by(RequestDB.ngay_tao.desc())

            if loai_mau is not None:
                query = query.filter(RequestDB.loai_mau == loai_mau)

            if batch_id is not None:
                query = query.filter(RequestDB.batch_id == batch_id)

            if latest_approved_only:
                query = query.filter(RequestDB.is_latest_approved == True)

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

    def get_requests_by_bien_so(self, bien_so: str) -> List[RequestInDB]:
        """
        Get all requests for a specific license plate (all versions)

        Args:
            bien_so: License plate number

        Returns:
            List of all requests for this plate, ordered by version desc
        """
        db = self._get_db()
        try:
            from sqlalchemy.orm import joinedload

            db_requests = db.query(RequestDB)\
                .options(joinedload(RequestDB.batch))\
                .filter(RequestDB.bien_so == bien_so)\
                .order_by(RequestDB.loai_mau, RequestDB.version.desc())\
                .all()

            return [self._db_to_pydantic(req) for req in db_requests]

        finally:
            db.close()

    def get_requests_by_cccd(self, cccd: str) -> List[RequestInDB]:
        """
        Get all requests for vehicles owned by this CCCD

        Args:
            cccd: CCCD number

        Returns:
            List of all requests for vehicles with this CCCD as owner
        """
        db = self._get_db()
        try:
            from sqlalchemy.orm import joinedload

            db_requests = db.query(RequestDB)\
                .options(joinedload(RequestDB.batch))\
                .filter(RequestDB.ma_so_thue_chu_xe == cccd)\
                .order_by(RequestDB.bien_so, RequestDB.loai_mau, RequestDB.version.desc())\
                .all()

            return [self._db_to_pydantic(req) for req in db_requests]

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

            # Mark this as the latest approved version for this bien_so + loai_mau
            # First, unmark all other requests for same bien_so + loai_mau
            db.query(RequestDB).filter(
                RequestDB.bien_so == db_request.bien_so,
                RequestDB.loai_mau == db_request.loai_mau,
                RequestDB.id != request_id
            ).update({"is_latest_approved": False})

            # Then mark this one as latest approved
            db_request.is_latest_approved = True

            db.commit()

            logger.info(f"Request {request_id} v{db_request.version} approved by {admin_username} and marked as latest approved")
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
