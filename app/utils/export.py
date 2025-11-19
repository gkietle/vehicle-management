import pandas as pd
from pathlib import Path
from typing import List
from datetime import datetime
from app.models import RequestInDB
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def export_requests_to_excel(requests: List[RequestInDB], loai_mau: int) -> Path:
    """
    Export requests to Excel file matching the form template

    Args:
        requests: List of requests to export
        loai_mau: Form template number (1-10)

    Returns:
        Path to exported Excel file
    """
    # Create output directory
    output_dir = settings.REQUESTS_DIR / "exports"
    output_dir.mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"Mau_{loai_mau}_Export_{timestamp}.xlsx"

    # Prepare data based on form type
    data = _prepare_export_data(requests, loai_mau)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Write to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add header rows based on template
        _format_excel_header(worksheet, loai_mau)

    logger.info(f"Exported {len(requests)} requests to {output_file}")
    return output_file


def _prepare_export_data(requests: List[RequestInDB], loai_mau: int) -> List[dict]:
    """Prepare data for export based on form type"""

    data = []

    for idx, req in enumerate(requests, 1):
        row = {
            "STT": idx,
            "Biển số": req.bien_so,
            "Loại xe": req.loai_xe or "",
            "Chủ xe": req.chu_xe or "",
            "Địa chỉ của chủ xe": req.dia_chi_chu_xe or "",
            "Số Điện thoại chủ xe": req.so_dien_thoai_chu_xe or "",
        }

        # Add columns based on form type
        if loai_mau in [1, 6]:
            # Form 1/6: Vehicle and owner match
            row["Mã số thuế/Quyết định thành lập của chủ xe"] = req.ma_so_thue_chu_xe or ""
            row["Tình trạng phương tiện (tốt/hỏng)"] = req.tinh_trang_xe or ""
            row["Ghi chú"] = req.ghi_chu or ""

        elif loai_mau in [2, 3, 4, 7, 8, 9]:
            # Forms 2-4, 7-9: Ownership changes
            row["Mã số thuế/Quyết định thành lập của chủ xe"] = req.ma_so_thue_chu_xe or ""
            row["Tên người mua/ được cho/tặng/thừa kế hoặc người đang sử dụng xe và địa chỉ hiện tại"] = req.ten_nguoi_mua or ""
            row["Số CCCD/mã số thuế/QĐ thành lập người mua/đang sử dụng"] = req.so_cccd_nguoi_mua or ""
            row["Số Điện thoại người mua... hoặc người đang sử dụng xe"] = req.so_dien_thoai_nguoi_mua or ""
            row["Bản sao chứng từ chuyển nhượng (nếu có)"] = ""

        elif loai_mau in [5, 10]:
            # Forms 5/10: New vehicle not in list
            row["Số khung, số máy của xe"] = f"{req.so_khung or ''}, {req.so_may or ''}"
            row["Mã số thuế/Quyết định thành lập của chủ xe"] = req.ma_so_thue_chu_xe or ""
            row["Tình trạng phương tiện (tốt/hỏng)"] = req.tinh_trang_xe or ""
            row["Ghi chú"] = req.ghi_chu or ""

        data.append(row)

    return data


def _format_excel_header(worksheet, loai_mau: int):
    """Format Excel header to match template"""
    # This is a simplified version
    # In production, you would copy the exact formatting from the template files

    # Add title rows
    worksheet.insert_rows(1, 3)

    # Merge cells for title
    worksheet.merge_cells('A1:J1')
    worksheet['A1'] = "Phụ lục 1: DANH SÁCH CỦA CƠ QUAN ĐĂNG KÝ GỬI CÔNG AN CẤP XÃ ĐỂ\nRÀ SOÁT, CẬP NHẬT VÀ BỔ SUNG DỮ LIỆU ĐĂNG KÝ XE; GIẤY PHÉP LÁI XE"

    # Section title
    if loai_mau <= 5:
        worksheet.merge_cells('A2:J2')
        worksheet['A2'] = "I. DANH SÁCH XE NỀN MÀU XANH, CHỮ VÀ SỐ MÀU TRẮNG"
    else:
        worksheet.merge_cells('A2:J2')
        worksheet['A2'] = "II. DANH SÁCH XE NỀN MÀU TRẮNG/VÀNG, CHỮ VÀ SỐ MÀU ĐEN"

    # Form name
    form_names = {
        1: "Mẫu 1: DANH SÁCH XE, CHỦ XE ĐÚNG VỚI DANH SÁCH CƠ QUAN ĐĂNG KÝ CUNG CẤP",
        2: "Mẫu 2: DANH SÁCH CÓ CHỦ XE NHƯNG KHÔNG CÓ XE TẠI ĐỊA BÀN",
        3: "Mẫu 3: DANH SÁCH CÓ XE NHƯNG KHÔNG CÓ CHỦ XE TẠI ĐỊA BÀN",
        4: "Mẫu 4: DANH SÁCH KHÔNG CÓ XE, KHÔNG CÓ CHỦ XE TẠI ĐỊA BÀN",
        5: "Mẫu 5: XE KHÔNG NẰM TRONG DANH SÁCH",
        6: "Mẫu 6: DANH SÁCH XE, CHỦ XE ĐÚNG VỚI DANH SÁCH CƠ QUAN ĐĂNG KÝ CUNG CẤP",
        7: "Mẫu 7: DANH SÁCH CÓ CHỦ XE NHƯNG KHÔNG CÓ XE TẠI ĐỊA BÀN",
        8: "Mẫu 8: DANH SÁCH CÓ XE NHƯNG KHÔNG CÓ CHỦ XE TẠI ĐỊA BÀN",
        9: "Mẫu 9: DANH SÁCH KHÔNG CÓ XE, KHÔNG CÓ CHỦ XE TẠI ĐỊA BÀN",
        10: "Mẫu 10: XE KHÔNG NẰM TRONG DANH SÁCH"
    }

    worksheet.merge_cells('A3:J3')
    worksheet['A3'] = form_names.get(loai_mau, f"Mẫu {loai_mau}")

    # Apply basic formatting
    for row in worksheet.iter_rows(min_row=1, max_row=3):
        for cell in row:
            cell.font = cell.font.copy(bold=True)
            cell.alignment = cell.alignment.copy(horizontal='center', vertical='center')
