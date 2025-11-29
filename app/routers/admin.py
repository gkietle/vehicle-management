from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import settings
from app.services.request_service import request_service
from app.services.vehicle_service import vehicle_service
from app.services.batch_service import batch_service
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))
security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    correct_username = secrets.compare_digest(
        credentials.username, settings.ADMIN_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.ADMIN_PASSWORD
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    username: str = Depends(verify_admin)
):
    """Admin dashboard"""
    # Get statistics
    request_stats = request_service.get_statistics()
    vehicle_stats = vehicle_service.get_statistics()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "title": "Trang quản trị",
            "username": username,
            "request_stats": request_stats,
            "vehicle_stats": vehicle_stats
        }
    )


@router.get("/yeu-cau", response_class=HTMLResponse)
async def admin_requests(
    request: Request,
    loai_mau: int = None,
    username: str = Depends(verify_admin)
):
    """View all requests"""
    # Get requests (filtered by form type if specified)
    requests = request_service.get_all_requests(loai_mau=loai_mau)

    return templates.TemplateResponse(
        "admin/requests.html",
        {
            "request": request,
            "title": "Danh sách yêu cầu",
            "username": username,
            "requests": requests,
            "loai_mau": loai_mau
        }
    )


@router.get("/export/mau-{loai_mau}")
async def export_requests(
    loai_mau: int,
    username: str = Depends(verify_admin)
):
    """Export requests to Excel for specific form (from active batch only)"""
    try:
        from app.utils.export import export_requests_to_excel

        # Get active batch
        active_batch = batch_service.get_active_batch()

        if not active_batch:
            raise HTTPException(
                status_code=400,
                detail="Không có đợt dữ liệu nào đang kích hoạt"
            )

        # Get LATEST APPROVED requests for this form from active batch only
        requests = request_service.get_all_requests(
            loai_mau=loai_mau,
            batch_id=active_batch.id,
            latest_approved_only=True  # Only export latest approved versions
        )

        if not requests:
            raise HTTPException(
                status_code=404,
                detail=f"Không có yêu cầu đã duyệt (version mới nhất) nào cho mẫu {loai_mau} trong đợt {active_batch.name}"
            )

        # Export to Excel
        output_file = export_requests_to_excel(requests, loai_mau)

        return FileResponse(
            path=output_file,
            filename=f"Mau_{loai_mau}_{active_batch.name}_YeuCau_{len(requests)}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        logger.error(f"Error exporting requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{request_id}/approve")
async def approve_request(
    request_id: str,
    username: str = Depends(verify_admin)
):
    """Approve a request"""
    success = request_service.approve_request(request_id, username)

    if success:
        return {"success": True, "message": f"Đã phê duyệt yêu cầu {request_id}"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Không thể phê duyệt yêu cầu này"
        )


@router.post("/request/{request_id}/reject")
async def reject_request(
    request_id: str,
    reason: str = "",
    username: str = Depends(verify_admin)
):
    """Reject a request"""
    success = request_service.reject_request(request_id, username, reason)

    if success:
        return {"success": True, "message": f"Đã từ chối yêu cầu {request_id}"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Không thể từ chối yêu cầu này"
        )


@router.post("/request/{request_id}/mark-processed")
async def mark_request_processed(
    request_id: str,
    username: str = Depends(verify_admin)
):
    """Mark request as processed"""
    success = request_service.mark_as_processed(request_id)

    if success:
        return {"success": True, "message": f"Đã đánh dấu yêu cầu {request_id} là đã xử lý"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Không thể đánh dấu yêu cầu này"
        )


@router.get("/request/{request_id}", response_class=HTMLResponse)
async def view_request_detail(
    request: Request,
    request_id: str,
    username: str = Depends(verify_admin)
):
    """View request detail"""
    req = request_service.get_request_by_id(request_id)

    if not req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu")

    return templates.TemplateResponse(
        "admin/request_detail.html",
        {
            "request": request,
            "title": f"Chi tiết yêu cầu {request_id}",
            "username": username,
            "req": req
        }
    )


# ========== BATCH MANAGEMENT ENDPOINTS ==========

@router.get("/batches", response_class=HTMLResponse)
async def batches_page(
    request: Request,
    username: str = Depends(verify_admin)
):
    """Batch management page"""
    batches = batch_service.get_all_batches()
    active_batch = batch_service.get_active_batch()

    return templates.TemplateResponse(
        "admin/batches.html",
        {
            "request": request,
            "title": "Quản lý đợt dữ liệu",
            "username": username,
            "batches": batches,
            "active_batch": active_batch
        }
    )


@router.post("/batches/create")
async def create_batch(
    name: str = Form(...),
    description: str = Form(""),
    username: str = Depends(verify_admin)
):
    """Create a new batch"""
    try:
        batch = batch_service.create_batch(name, description)
        return {"success": True, "message": f"Đã tạo đợt '{name}'", "batch_id": batch.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating batch: {e}")
        raise HTTPException(status_code=500, detail="Lỗi khi tạo đợt dữ liệu")


@router.post("/batches/{batch_id}/activate")
async def activate_batch(
    batch_id: int,
    username: str = Depends(verify_admin)
):
    """Set a batch as active"""
    success = batch_service.set_active_batch(batch_id)

    if success:
        # Reload vehicle data files
        vehicle_service.reload_data_files()
        return {"success": True, "message": f"Đã kích hoạt đợt ID {batch_id}"}
    else:
        raise HTTPException(status_code=400, detail="Không thể kích hoạt đợt này")


@router.post("/batches/{batch_id}/upload")
async def upload_file(
    batch_id: int,
    file: UploadFile = File(...),
    username: str = Depends(verify_admin)
):
    """Upload a file to a batch"""
    try:
        # Read file content
        content = await file.read()

        # Upload to batch
        data_file = batch_service.upload_file_to_batch(batch_id, content, file.filename)

        return {
            "success": True,
            "message": f"Đã upload file '{file.filename}'",
            "file_id": data_file.id,
            "file_size": data_file.file_size,
            "sheet_count": data_file.sheet_count
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/batches/{batch_id}")
async def delete_batch(
    batch_id: int,
    username: str = Depends(verify_admin)
):
    """Delete a batch"""
    success = batch_service.delete_batch(batch_id)

    if success:
        return {"success": True, "message": f"Đã xóa đợt ID {batch_id}"}
    else:
        raise HTTPException(status_code=400, detail="Không thể xóa đợt này (có thể đang active)")


@router.delete("/batches/files/{file_id}")
async def delete_file(
    file_id: int,
    username: str = Depends(verify_admin)
):
    """Delete a file from a batch"""
    success = batch_service.delete_file(file_id)

    if success:
        return {"success": True, "message": f"Đã xóa file ID {file_id}"}
    else:
        raise HTTPException(status_code=400, detail="Không thể xóa file này")


@router.get("/batches/{batch_id}/files")
async def get_batch_files(
    batch_id: int,
    username: str = Depends(verify_admin)
):
    """Get list of files in a batch"""
    files = batch_service.get_batch_files(batch_id)

    return {
        "success": True,
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "file_size": f.file_size,
                "sheet_count": f.sheet_count,
                "record_count": f.record_count,
                "uploaded_at": f.uploaded_at.strftime("%d/%m/%Y %H:%M")
            }
            for f in files
        ]
    }


@router.get("/batches/{batch_id}/data", response_class=HTMLResponse)
async def view_batch_data(
    request: Request,
    batch_id: int,
    username: str = Depends(verify_admin)
):
    """View batch data page"""
    batch = batch_service.get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy đợt dữ liệu")

    return templates.TemplateResponse(
        "admin/batch_data.html",
        {
            "request": request,
            "title": f"Dữ liệu - {batch.name}",
            "username": username,
            "batch": batch
        }
    )


@router.get("/batches/{batch_id}/records")
async def get_batch_records(
    batch_id: int,
    search: str = "",
    page: int = 1,
    page_size: int = 50,
    username: str = Depends(verify_admin)
):
    """Get records from a batch with pagination and search"""
    offset = (page - 1) * page_size
    records, total = batch_service.get_batch_records(batch_id, search if search else None, page_size, offset)

    total_pages = (total + page_size - 1) // page_size

    return {
        "success": True,
        "records": records,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }
