import pandas as pd
import os

print("="*80)
print("PHÂN TÍCH CÁC BIỂU MẪU THAY ĐỔI THÔNG TIN")
print("="*80)

form_dir = "./data/bieumauthaydoithongtin"
form_files = sorted([f for f in os.listdir(form_dir) if f.endswith('.xlsx') and not f.startswith('.')])

for form_file in form_files:
    file_path = os.path.join(form_dir, form_file)
    print(f"\n{'='*80}")
    print(f"BIỂU MẪU: {form_file}")
    print(f"{'='*80}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Số sheet: {len(xls.sheet_names)}")
        print(f"Tên các sheet: {', '.join(xls.sheet_names)}")

        for sheet_name in xls.sheet_names:
            # Read first 10 rows to understand structure
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Số cột: {df.shape[1]}")

            print(f"\nCác cột:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            # Show all data (max 10 rows)
            print(f"\nDữ liệu mẫu:")
            print(df.to_string(index=False))
            print()

    except Exception as e:
        print(f"❌ LỖI: {str(e)}")

print("\n" + "="*80)
print("HOÀN TẤT PHÂN TÍCH!")
print("="*80)
