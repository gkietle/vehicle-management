from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.models import SearchResponse, RequestCreate, RequestResponse
from app.services.vehicle_service import vehicle_service
from app.services.request_service import request_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))


@router.get("/tra-cuu", response_class=HTMLResponse)
async def tra_cuu_page(request: Request):
    """Vehicle search page"""
    return templates.TemplateResponse(
        "tra-cuu.html",
        {"request": request, "title": "Tra cứu biển số xe"}
    )


@router.post("/api/search")
async def search_vehicle(
    bien_so: str = Form(None),
    cccd: str = Form(None),
    search_type: str = Form("bien_so")
) -> SearchResponse:
    """
    API endpoint to search for vehicle by license plate or CCCD

    Args:
        bien_so: License plate number (optional)
        cccd: CCCD number (optional)
        search_type: Type of search - "bien_so" or "cccd"

    Returns:
        SearchResponse with vehicle info if found
    """
    try:
        if search_type == "cccd" and cccd:
            logger.info(f"Searching for vehicles with CCCD: {cccd}")

            # Search by CCCD
            vehicles = vehicle_service.search_by_cccd(cccd)

            if vehicles:
                return SearchResponse(
                    found=True,
                    message=f"Tìm thấy {len(vehicles)} phương tiện",
                    vehicle=vehicles[0] if len(vehicles) == 1 else None,
                    vehicles=vehicles
                )
            else:
                return SearchResponse(
                    found=False,
                    message=f"Không tìm thấy phương tiện nào với CCCD {cccd}",
                    vehicle=None
                )

        elif search_type == "bien_so" and bien_so:
            logger.info(f"Searching for vehicle: {bien_so}")

            # Search by license plate
            vehicle = vehicle_service.search_by_bien_so(bien_so)

            if vehicle:
                return SearchResponse(
                    found=True,
                    message="Tìm thấy thông tin xe",
                    vehicle=vehicle
                )
            else:
                return SearchResponse(
                    found=False,
                    message=f"Không tìm thấy thông tin cho biển số {bien_so}",
                    vehicle=None
                )
        else:
            return SearchResponse(
                found=False,
                message="Vui lòng nhập biển số xe hoặc số CCCD",
                vehicle=None
            )

    except Exception as e:
        logger.error(f"Error searching vehicle: {e}")
        return SearchResponse(
            found=False,
            message=f"Lỗi khi tìm kiếm: {str(e)}",
            vehicle=None
        )


@router.get("/yeu-cau/mau-{loai_mau}", response_class=HTMLResponse)
async def yeu_cau_form(request: Request, loai_mau: int, bien_so: str = ""):
    """
    Display request form for specific template

    Args:
        loai_mau: Form template number (1-10)
        bien_so: Pre-filled license plate number
    """
    if loai_mau < 1 or loai_mau > 10:
        return HTMLResponse(content="Mẫu không hợp lệ", status_code=400)

    # Get form template name
    form_templates = {
        1: "Xe và chủ xe đúng với danh sách",
        2: "Có chủ xe nhưng không có xe tại địa bàn",
        3: "Có xe nhưng không có chủ xe tại địa bàn",
        4: "Không có xe và chủ xe tại địa bàn",
        5: "Xe không nằm trong danh sách",
        6: "Xe và chủ xe đúng với danh sách (Biển trắng/vàng)",
        7: "Có chủ xe nhưng không có xe tại địa bàn (Biển trắng/vàng)",
        8: "Có xe nhưng không có chủ xe tại địa bàn (Biển trắng/vàng)",
        9: "Không có xe và chủ xe tại địa bàn (Biển trắng/vàng)",
        10: "Xe không nằm trong danh sách (Biển trắng/vàng)"
    }

    # Get vehicle info if bien_so provided
    vehicle = None
    if bien_so:
        vehicle = vehicle_service.search_by_bien_so(bien_so)

    return templates.TemplateResponse(
        "yeu-cau/form.html",
        {
            "request": request,
            "title": f"Mẫu {loai_mau}: {form_templates[loai_mau]}",
            "loai_mau": loai_mau,
            "form_name": form_templates[loai_mau],
            "bien_so": bien_so,
            "vehicle": vehicle
        }
    )


@router.post("/yeu-cau/review")
async def review_request(request: Request):
    """Review page before submitting request"""
    # Get form data
    form_data = await request.form()

    # Form template names
    form_templates = {
        1: "Xe và chủ xe đúng với danh sách",
        2: "Có chủ xe nhưng không có xe tại địa bàn",
        3: "Có xe nhưng không có chủ xe tại địa bàn",
        4: "Không có xe và chủ xe tại địa bàn",
        5: "Xe không nằm trong danh sách",
        6: "Xe và chủ xe đúng với danh sách (Biển trắng/vàng)",
        7: "Có chủ xe nhưng không có xe tại địa bàn (Biển trắng/vàng)",
        8: "Có xe nhưng không có chủ xe tại địa bàn (Biển trắng/vàng)",
        9: "Không có xe và chủ xe tại địa bàn (Biển trắng/vàng)",
        10: "Xe không nằm trong danh sách (Biển trắng/vàng)"
    }

    loai_mau = int(form_data.get("loai_mau", 1))

    return templates.TemplateResponse(
        "yeu-cau/review.html",
        {
            "request": request,
            "title": "Kiểm tra lại thông tin",
            "form_name": form_templates.get(loai_mau, ""),
            "loai_mau": loai_mau,
            "bien_so": form_data.get("bien_so", ""),
            "loai_xe": form_data.get("loai_xe", ""),
            "chu_xe": form_data.get("chu_xe", ""),
            "dia_chi_chu_xe": form_data.get("dia_chi_chu_xe", ""),
            "so_dien_thoai_chu_xe": form_data.get("so_dien_thoai_chu_xe", ""),
            "ma_so_thue_chu_xe": form_data.get("ma_so_thue_chu_xe", ""),
            "ten_nguoi_mua": form_data.get("ten_nguoi_mua", ""),
            "dia_chi_nguoi_mua": form_data.get("dia_chi_nguoi_mua", ""),
            "so_cccd_nguoi_mua": form_data.get("so_cccd_nguoi_mua", ""),
            "so_dien_thoai_nguoi_mua": form_data.get("so_dien_thoai_nguoi_mua", ""),
            "so_khung": form_data.get("so_khung", ""),
            "so_may": form_data.get("so_may", ""),
            "tinh_trang_xe": form_data.get("tinh_trang_xe", ""),
            "ghi_chu": form_data.get("ghi_chu", ""),
        }
    )


@router.post("/api/request/create")
async def create_request(request_data: RequestCreate) -> RequestResponse:
    """
    Create a new update request

    Args:
        request_data: Request data

    Returns:
        RequestResponse with success status and request ID
    """
    try:
        logger.info(f"Creating request for vehicle: {request_data.bien_so}, form: {request_data.loai_mau}")

        # Create request
        created_request = request_service.create_request(request_data)

        return RequestResponse(
            success=True,
            message="Yêu cầu đã được gửi thành công",
            request_id=created_request.id
        )

    except Exception as e:
        logger.error(f"Error creating request: {e}")
        return RequestResponse(
            success=False,
            message=f"Lỗi khi tạo yêu cầu: {str(e)}",
            request_id=None
        )


@router.get("/yeu-cau/thanh-cong", response_class=HTMLResponse)
async def request_success(request: Request, request_id: str = ""):
    """Success page after submitting request"""
    return templates.TemplateResponse(
        "yeu-cau/success.html",
        {
            "request": request,
            "title": "Gửi yêu cầu thành công",
            "request_id": request_id
        }
    )


@router.get("/tra-cuu-yeu-cau", response_class=HTMLResponse)
async def tra_cuu_yeu_cau_page(request: Request):
    """Request status lookup page"""
    return templates.TemplateResponse(
        "tra-cuu-yeu-cau.html",
        {
            "request": request,
            "title": "Tra cứu trạng thái yêu cầu"
        }
    )


@router.get("/api/request/status/{request_id}")
async def get_request_status(request_id: str):
    """Get request status by ID"""
    try:
        req = request_service.get_request_by_id(request_id)

        if req:
            return {
                "success": True,
                "request": {
                    "id": req.id,
                    "bien_so": req.bien_so,
                    "loai_xe": req.loai_xe,
                    "chu_xe": req.chu_xe,
                    "ngay_tao": req.ngay_tao.strftime("%d/%m/%Y %H:%M") if req.ngay_tao else "",
                    "trang_thai": req.trang_thai,
                    "nguoi_duyet": req.nguoi_duyet,
                    "ngay_duyet": req.ngay_duyet.strftime("%d/%m/%Y %H:%M") if req.ngay_duyet else None,
                    "ly_do_tu_choi": req.ly_do_tu_choi,
                    "ghi_chu": req.ghi_chu
                }
            }
        else:
            return {
                "success": False,
                "message": "Không tìm thấy yêu cầu"
            }

    except Exception as e:
        logger.error(f"Error getting request status: {e}")
        return {
            "success": False,
            "message": f"Lỗi khi tra cứu: {str(e)}"
        }
