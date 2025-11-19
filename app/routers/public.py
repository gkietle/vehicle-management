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
async def search_vehicle(bien_so: str = Form(...)) -> SearchResponse:
    """
    API endpoint to search for vehicle by license plate

    Args:
        bien_so: License plate number

    Returns:
        SearchResponse with vehicle info if found
    """
    try:
        logger.info(f"Searching for vehicle: {bien_so}")

        # Search in vehicle data
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
