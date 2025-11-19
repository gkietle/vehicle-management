import pandas as pd
import os
from pathlib import Path

def analyze_excel_file(file_path, file_type=""):
    """Analyze Excel file structure and content"""
    print(f"\n{'='*80}")
    print(f"FILE: {os.path.basename(file_path)}")
    print(f"TYPE: {file_type}")
    print(f"{'='*80}")

    try:
        # Read Excel file
        xls = pd.ExcelFile(file_path)
        print(f"Number of sheets: {len(xls.sheet_names)}")
        print(f"Sheet names: {xls.sheet_names}")

        # Analyze each sheet
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"\nColumns:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            # Show sample data (first 3 rows)
            print(f"\nSample data (first 3 rows):")
            print(df.head(3).to_string())

            # Check for missing values
            missing = df.isnull().sum()
            if missing.any():
                print(f"\nMissing values:")
                print(missing[missing > 0])

        return {
            'file': os.path.basename(file_path),
            'sheets': xls.sheet_names,
            'columns': list(df.columns) if len(xls.sheet_names) > 0 else []
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

# Analyze vehicle data files
print("\n" + "="*80)
print("PHÂN TÍCH DỮ LIỆU PHƯƠNG TIỆN")
print("="*80)

vehicle_files = [
    ("./data/dulieuphuongtien/1.BIEN_XANH_TINH_DONG_NAI 60 LOC MOTO (Long Bình).xlsx", "Biển Xanh"),
    ("./data/dulieuphuongtien/2. MOTO_BIEN_TRANG_VANG_KHONG_C06_TINH_DONG_NAI/60.1 Long Bình.xlsx", "Biển Trắng Vàng (Không C06)"),
    ("./data/dulieuphuongtien/3. MOTO_BIEN_TRANG_VANG_CO__C06_TINH_DONG_NAI/60.1 Long Bình.xlsx", "Biển Trắng Vàng (Có C06)"),
]

vehicle_structures = []
for file_path, file_type in vehicle_files:
    if os.path.exists(file_path):
        result = analyze_excel_file(file_path, file_type)
        if result:
            vehicle_structures.append(result)

# Analyze form templates
print("\n\n" + "="*80)
print("PHÂN TÍCH BIỂU MẪU THAY ĐỔI THÔNG TIN")
print("="*80)

form_files = [
    "./data/bieumauthaydoithongtin/Mẫu 1.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 2.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 3.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 4.xlsx",
    "./data/bieumauthaydoithongtin/Mẫu 5.xlsx",
]

form_structures = []
for file_path in form_files:
    if os.path.exists(file_path):
        result = analyze_excel_file(file_path, "Biểu mẫu")
        if result:
            form_structures.append(result)

# Compare structures
print("\n\n" + "="*80)
print("SO SÁNH CẤU TRÚC DỮ LIỆU")
print("="*80)

print("\n--- DỮ LIỆU PHƯƠNG TIỆN ---")
if len(vehicle_structures) > 1:
    base_cols = set(vehicle_structures[0]['columns'])
    all_same = True
    for i, struct in enumerate(vehicle_structures[1:], 1):
        current_cols = set(struct['columns'])
        if base_cols != current_cols:
            all_same = False
            print(f"\n❌ File '{struct['file']}' có cấu trúc KHÁC:")
            print(f"  Thiếu: {base_cols - current_cols}")
            print(f"  Thừa: {current_cols - base_cols}")
        else:
            print(f"✅ File '{struct['file']}' có cấu trúc GIỐNG NHAU")

    if all_same:
        print("\n✅ TẤT CẢ FILE DỮ LIỆU PHƯƠNG TIỆN CÓ CÙNG CẤU TRÚC!")
else:
    print("Không đủ file để so sánh")

print("\n--- BIỂU MẪU ---")
for struct in form_structures:
    print(f"\n{struct['file']}:")
    print(f"  Số sheet: {len(struct['sheets'])}")
    print(f"  Tên sheet: {struct['sheets']}")
