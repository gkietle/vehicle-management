import pandas as pd
from pathlib import Path
from typing import List
from datetime import datetime
from app.models import RequestInDB
from app.config import settings
import logging
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side
import shutil

logger = logging.getLogger(__name__)


def export_requests_to_excel(requests: List[RequestInDB], loai_mau: int) -> Path:
    """
    Export requests to Excel file matching the form template

    Args:
        requests: List of requests to export
        loai_mau: Form template number (6-10 for white/yellow plates)

    Returns:
        Path to exported Excel file
    """
    # Create output directory
    output_dir = settings.REQUESTS_DIR / "exports"
    output_dir.mkdir(exist_ok=True)

    # Copy template file
    template_file = Path(__file__).parent.parent.parent / "update_2911" / f"Mẫu {loai_mau}.xlsx"

    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"Mau_{loai_mau}_Export_{timestamp}.xlsx"

    # Copy template
    shutil.copy(template_file, output_file)

    # Load workbook
    wb = load_workbook(output_file)
    ws = wb.active

    # Find data start row (after headers)
    data_start_row = 4  # Row 4 is headers, Row 5 starts data

    # Prepare and write data
    data_rows = _prepare_export_data(requests, loai_mau)

    for idx, row_data in enumerate(data_rows, start=data_start_row + 1):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=idx, column=col_idx)
            cell.value = value
            # Apply basic formatting
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Save workbook
    wb.save(output_file)
    logger.info(f"Exported {len(requests)} requests to {output_file}")
    return output_file


def _prepare_export_data(requests: List[RequestInDB], loai_mau: int) -> List[List]:
    """Prepare data rows for export based on form type"""
    data_rows = []

    for idx, req in enumerate(requests, 1):
        if loai_mau == 6:
            # Mẫu 6: Xe và chủ xe đúng
            row = [
                idx,  # STT
                req.bien_so or "",  # Biển số
                req.mau_bien or "",  # Màu biển
                req.loai_xe or "",  # Loại xe
                req.chu_xe or "",  # Chủ xe
                req.dia_chi_chu_xe or "",  # Địa chỉ thường trú, địa chỉ hiện tại
                req.so_khung or "",  # Số khung
                req.so_may or "",  # Số máy
                req.so_dien_thoai_chu_xe or "",  # Số Điện thoại
                req.ma_so_thue_chu_xe or "",  # Số CCCD/mã số thuế
                req.ngay_cap_cccd_chu_xe or "",  # Ngày cấp CCCD
                req.so_gplx_chu_xe or "",  # Số GPLX
                req.ngay_cap_gplx_chu_xe or "",  # Ngày cấp GPLX
                req.co_quan_cap_gplx_chu_xe or "",  # Cơ quan cấp GPLX
                req.tinh_trang_xe or "",  # Tình trạng phương tiện
                req.ghi_chu or ""  # Ghi chú
            ]

        elif loai_mau == 7:
            # Mẫu 7: Có chủ xe, không có xe
            row = [
                idx,  # STT
                req.bien_so or "",  # Biển số
                req.mau_bien or "",  # Màu biển
                req.loai_xe or "",  # Loại xe
                req.chu_xe or "",  # Chủ xe
                req.dia_chi_chu_xe or "",  # Địa chỉ thường trú, địa chỉ hiện tại
                req.so_dien_thoai_chu_xe or "",  # Số Điện thoại chủ xe
                req.ma_so_thue_chu_xe or "",  # Số CCCD/mã số thuế của chủ xe
                req.ngay_cap_cccd_chu_xe or "",  # Ngày cấp CCCD
                req.so_gplx_chu_xe or "",  # Số GPLX
                req.ngay_cap_gplx_chu_xe or "",  # Ngày cấp GPLX
                req.co_quan_cap_gplx_chu_xe or "",  # Cơ quan cấp GPLX
                req.ten_nguoi_mua or "",  # Tên người mua/đang sử dụng
                req.ban_sao_chuyen_nhuong or "",  # Bản sao chứng từ chuyển nhượng
                req.so_dien_thoai_nguoi_mua or "",  # Số Điện thoại người mua
                req.so_cccd_nguoi_mua or "",  # Số CCCD/mã số thuế người mua
                req.ngay_cap_cccd_nguoi_mua or ""  # Ngày cấp CCCD người mua
            ]

        elif loai_mau == 8:
            # Mẫu 8: Có xe, không có chủ xe
            row = [
                idx,  # STT
                req.bien_so or "",  # Biển số
                req.mau_bien or "",  # Màu biển
                req.loai_xe or "",  # Loại xe
                req.chu_xe or "",  # Chủ xe
                req.dia_chi_chu_xe or "",  # Địa chỉ thường trú, địa chỉ hiện tại
                req.so_dien_thoai_chu_xe or "",  # Số Điện thoại chủ xe
                req.ma_so_thue_chu_xe or "",  # Số CCCD/mã số thuế của chủ xe
                req.ngay_cap_cccd_chu_xe or "",  # Ngày cấp CCCD của chủ xe
                req.so_gplx_chu_xe or "",  # Số GPLX của người đang sử dụng xe
                req.ngay_cap_gplx_chu_xe or "",  # Ngày cấp GPLX của chủ xe
                req.co_quan_cap_gplx_chu_xe or "",  # Cơ quan cấp GPLX của chủ xe
                req.ten_nguoi_mua or "",  # Tên người mua/đang sử dụng
                req.so_dien_thoai_nguoi_mua or "",  # Số Điện thoại người mua
                req.so_cccd_nguoi_mua or "",  # Số CCCD/mã số thuế người mua
                req.ngay_cap_cccd_nguoi_mua or "",  # Ngày cấp CCCD người mua
                req.ban_sao_chuyen_nhuong or ""  # Bản sao chứng từ chuyển nhượng
            ]

        elif loai_mau == 9:
            # Mẫu 9: Không có xe, không có chủ xe
            row = [
                idx,  # STT
                req.bien_so or "",  # Biển số
                req.mau_bien or "",  # Màu biển
                req.loai_xe or "",  # Loại xe
                req.chu_xe or "",  # Chủ xe
                req.dia_chi_chu_xe or "",  # Địa chỉ thường trú, địa chỉ hiện tại
                req.so_dien_thoai_chu_xe or "",  # Số Điện thoại của chủ xe
                req.ma_so_thue_chu_xe or "",  # Số CCCD/mã số thuế của chủ xe
                req.ngay_cap_cccd_chu_xe or "",  # Ngày cấp CCCD của chủ xe
                req.ten_nguoi_mua or "",  # Tên người mua/đang sử dụng
                req.so_dien_thoai_nguoi_mua or "",  # Số Điện thoại người mua
                req.so_cccd_nguoi_mua or "",  # Số CCCD/mã số thuế người mua
                req.ngay_cap_cccd_nguoi_mua or "",  # Ngày cấp CCCD người mua
                req.ban_sao_chuyen_nhuong or ""  # Bản sao chứng từ chuyển nhượng
            ]

        elif loai_mau == 10:
            # Mẫu 10: Xe không nằm trong danh sách
            row = [
                idx,  # STT
                req.bien_so or "",  # Biển số
                req.mau_bien or "",  # Màu biển
                req.loai_xe or "",  # Loại xe
                f"{req.chu_xe or ''} - {req.dia_chi_chu_xe or ''}",  # Chủ xe và địa chỉ
                f"{req.ten_nguoi_dang_su_dung or ''} - {req.dia_chi_nguoi_dang_su_dung or ''}",  # Người đang sử dụng và địa chỉ
                req.so_dien_thoai_chu_xe or "",  # Số Điện thoại của chủ xe
                req.ma_so_thue_chu_xe or "",  # Số CCCD/mã số thuế của chủ xe
                req.ngay_cap_cccd_chu_xe or "",  # Ngày cấp CCCD/mã số thuế của chủ xe
                req.so_gplx_chu_xe or "",  # Số GPLX của chủ xe
                req.ngay_cap_gplx_chu_xe or "",  # Ngày cấp GPLX của chủ xe
                req.co_quan_cap_gplx_chu_xe or "",  # Cơ quan cấp GPLX của chủ xe
                f"{req.ten_nguoi_ban or ''} - {req.dia_chi_nguoi_ban or ''}",  # Tên người bán xe và địa chỉ
                req.so_dien_thoai_nguoi_ban or "",  # Số Điện thoại của người bán xe
                req.so_cccd_nguoi_ban or "",  # Số CCCD/mã số thuế người bán xe
                req.ngay_cap_cccd_nguoi_ban or "",  # Ngày cấp CCCD/mã số thuế người bán xe
                req.ban_sao_chuyen_nhuong or ""  # Bản sao chứng từ chuyển nhượng
            ]

        else:
            # Default fallback (for mẫu 1-5)
            row = [
                idx,
                req.bien_so or "",
                req.loai_xe or "",
                req.chu_xe or "",
                req.dia_chi_chu_xe or "",
                req.so_dien_thoai_chu_xe or "",
                req.ghi_chu or ""
            ]

        data_rows.append(row)

    return data_rows


def _format_excel_header(worksheet, loai_mau: int):
    """Format Excel header to match template - Not needed if using template copy"""
    pass
