import pandas as pd
import os

def quick_analyze(file_path, file_type=""):
    """Quick analysis - only read first 5 rows"""
    print(f"\n{'='*80}")
    print(f"FILE: {os.path.basename(file_path)}")
    print(f"TYPE: {file_type}")
    print(f"{'='*80}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Số sheet: {len(xls.sheet_names)}")
        print(f"Tên sheet: {', '.join(xls.sheet_names)}")

        for sheet_name in xls.sheet_names:
            # Only read first 5 rows for quick analysis
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Số cột: {df.shape[1]}")
            print(f"\nCác cột:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            print(f"\nDữ liệu mẫu (3 dòng đầu):")
            print(df.head(3).to_string(index=False))

        return list(df.columns)

    except Exception as e:
        print(f"❌ LỖI: {str(e)}")
        return None

print("="*80)
print("PHÂN TÍCH DỮ LIỆU PHƯƠNG TIỆN")
print("="*80)

# Vehicle data files
vehicles = [
    ("./data/dulieuphuongtien/1.BIEN_XANH_TINH_DONG_NAI 60 LOC MOTO (Long Bình).xlsx", "Biển Xanh"),
    ("./data/dulieuphuongtien/2. MOTO_BIEN_TRANG_VANG_KHONG_C06_TINH_DONG_NAI/60.1 Long Bình.xlsx", "Biển Trắng Vàng - Không C06"),
    ("./data/dulieuphuongtien/3. MOTO_BIEN_TRANG_VANG_CO__C06_TINH_DONG_NAI/60.1 Long Bình.xlsx", "Biển Trắng Vàng - Có C06"),
]

v_cols = []
for path, vtype in vehicles:
    if os.path.exists(path):
        cols = quick_analyze(path, vtype)
        if cols:
            v_cols.append((os.path.basename(path), cols))

print("\n\n" + "="*80)
print("PHÂN TÍCH BIỂU MẪU")
print("="*80)

forms = [
    "./data/bieumauthaydoithongtin/Mẫu 1.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 2.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 3.xlsx",
]

for path in forms:
    if os.path.exists(path):
        quick_analyze(path, "Biểu mẫu")

# Compare vehicle data structures
print("\n\n" + "="*80)
print("SO SÁNH CẤU TRÚC DỮ LIỆU XE")
print("="*80)

if len(v_cols) > 1:
    base = set(v_cols[0][1])
    print(f"\nCấu trúc chuẩn (từ {v_cols[0][0]}):")
    print(f"Số cột: {len(base)}")

    all_same = True
    for fname, cols in v_cols[1:]:
        current = set(cols)
        if base == current:
            print(f"\n✅ {fname}: GIỐNG CẤU TRÚC CHUẨN")
        else:
            all_same = False
            print(f"\n❌ {fname}: KHÁC CẤU TRÚC CHUẨN")
            missing = base - current
            extra = current - base
            if missing:
                print(f"  Thiếu cột: {missing}")
            if extra:
                print(f"  Thừa cột: {extra}")

    if all_same:
        print("\n" + "="*80)
        print("🎉 KẾT LUẬN: TẤT CẢ FILE DỮ LIỆU XE CÓ CÙNG CẤU TRÚC!")
        print("="*80)
