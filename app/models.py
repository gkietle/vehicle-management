from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class VehicleInfo(BaseModel):
    """Model for vehicle information"""
    bien_so: str = Field(..., description="Biển số xe")
    mau_bien: Optional[str] = Field(None, description="Màu biển (0=trắng/vàng, 1=xanh)")
    loai_xe: Optional[str] = Field(None, description="Loại xe")
    ten: Optional[str] = Field(None, description="Tên chủ xe")
    dia_chi_dang_ky_xe: Optional[str] = Field(None, description="Địa chỉ đăng ký xe")
    khu_pho: Optional[str] = Field(None, description="Khu phố")
    dia_chi_thuong_tru: Optional[str] = Field(None, description="Địa chỉ thường trú")
    noi_o_hien_tai: Optional[str] = Field(None, description="Nơi ở hiện tại")
    so_khung: Optional[str] = Field(None, description="Số khung")
    so_may: Optional[str] = Field(None, description="Số máy")
    so_dien_thoai: Optional[str] = Field(None, description="Số điện thoại")
    loai_giay_to: Optional[str] = Field(None, description="Loại giấy tờ")
    so_giay_to: Optional[str] = Field(None, description="Số giấy tờ")
    trang_thai_xe: Optional[str] = Field(None, description="Trạng thái xe")
    trang_thai_dang_ky: Optional[str] = Field(None, description="Trạng thái đăng ký")

    class Config:
        json_schema_extra = {
            "example": {
                "bien_so": "60B100129",
                "loai_xe": "Hai bánh từ 50-175cm3",
                "ten": "NGUYỄN VẠN A",
                "dia_chi_dang_ky_xe": "KP8A,Tân Biên,BH"
            }
        }


class RequestBase(BaseModel):
    """Base model for update requests"""
    bien_so: str
    loai_mau: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] = Field(..., description="Loại mẫu (1-10)")
    loai_xe: Optional[str] = None
    chu_xe: Optional[str] = None
    dia_chi_chu_xe: Optional[str] = None
    so_dien_thoai_chu_xe: Optional[str] = None
    ma_so_thue_chu_xe: Optional[str] = None

    # For forms 2, 3, 4
    ten_nguoi_mua: Optional[str] = None
    dia_chi_nguoi_mua: Optional[str] = None
    so_cccd_nguoi_mua: Optional[str] = None
    so_dien_thoai_nguoi_mua: Optional[str] = None

    # For form 5, 10 (new vehicle)
    so_khung: Optional[str] = None
    so_may: Optional[str] = None

    # Additional info
    tinh_trang_xe: Optional[str] = None
    ghi_chu: Optional[str] = None


class RequestCreate(RequestBase):
    """Model for creating new request"""
    pass


class RequestInDB(RequestBase):
    """Model for request in database"""
    id: str
    ngay_tao: datetime
    trang_thai: Literal["pending", "approved", "rejected", "processed"] = "pending"
    nguoi_duyet: Optional[str] = None  # Admin username
    ngay_duyet: Optional[datetime] = None  # Approval date
    ly_do_tu_choi: Optional[str] = None  # Rejection reason

    class Config:
        json_schema_extra = {
            "example": {
                "id": "REQ_20250119_001",
                "bien_so": "60B100129",
                "loai_mau": 1,
                "ngay_tao": "2025-01-19T10:30:00",
                "trang_thai": "pending",
                "nguoi_duyet": None,
                "ngay_duyet": None,
                "ly_do_tu_choi": None
            }
        }


class RequestResponse(BaseModel):
    """Response model for request operations"""
    success: bool
    message: str
    request_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for vehicle search"""
    found: bool
    message: str
    vehicle: Optional[VehicleInfo] = None
