# Hệ thống Tra cứu & Quản lý Phương tiện

Hệ thống web tra cứu thông tin phương tiện giao thông và quản lý yêu cầu cập nhật dữ liệu cho Phường Long Bình, Thành phố Biên Hòa, Tỉnh Đồng Nai.

## 🚀 Tính năng

### Người dân:
- ✅ Tra cứu thông tin xe theo biển số
- ✅ Xem thông tin chi tiết (chủ xe, địa chỉ, số khung, số máy...)
- ✅ Gửi yêu cầu cập nhật thông tin theo 10 biểu mẫu chuẩn
- ✅ Nhận mã số yêu cầu để theo dõi

### Quản trị viên:
- ✅ Xem dashboard tổng quan
- ✅ Quản lý danh sách yêu cầu
- ✅ Lọc yêu cầu theo từng biểu mẫu
- ✅ Export yêu cầu ra file Excel theo đúng format biểu mẫu
- ✅ Thống kê dữ liệu

## 📦 Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Frontend**: Jinja2 Templates + TailwindCSS
- **Data Processing**: pandas, openpyxl
- **Server**: Uvicorn

## 🔧 Cài đặt

### 1. Clone repository (hoặc có sẵn)

```bash
cd vehicle-mangement
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python3 run.py
```

Hoặc:

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Truy cập ứng dụng

- **Trang chủ**: http://localhost:8000
- **Tra cứu**: http://localhost:8000/tra-cuu
- **Admin Dashboard**: http://localhost:8000/admin/dashboard
  - Username: `admin`
  - Password: `admin123`
- **API Docs**: http://localhost:8000/docs

## 📁 Cấu trúc dự án

```
vehicle-mangement/
├── app/
│   ├── main.py              # FastAPI app chính
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── public.py        # Routes công khai
│   │   └── admin.py         # Routes quản trị
│   ├── services/
│   │   ├── vehicle_service.py   # Service tra cứu xe
│   │   └── request_service.py   # Service quản lý yêu cầu
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── tra-cuu.html
│   │   ├── yeu-cau/
│   │   └── admin/
│   ├── static/              # CSS, JS, images
│   └── utils/
│       └── export.py        # Export Excel utilities
├── data/
│   ├── dulieuphuongtien/   # Dữ liệu xe (Excel files)
│   └── bieumauthaydoithongtin/  # 10 biểu mẫu
├── requests/                # Lưu yêu cầu (JSON)
├── requirements.txt
├── run.py
└── README.md
```

## 📋 10 Biểu mẫu

### Biển Xanh (Mẫu 1-5):
1. **Mẫu 1**: Xe và chủ xe đúng với danh sách
2. **Mẫu 2**: Có chủ xe nhưng không có xe tại địa bàn
3. **Mẫu 3**: Có xe nhưng không có chủ xe tại địa bàn
4. **Mẫu 4**: Không có xe và chủ xe tại địa bàn
5. **Mẫu 5**: Xe không nằm trong danh sách

### Biển Trắng/Vàng (Mẫu 6-10):
6. **Mẫu 6**: Xe và chủ xe đúng với danh sách
7. **Mẫu 7**: Có chủ xe nhưng không có xe tại địa bàn
8. **Mẫu 8**: Có xe nhưng không có chủ xe tại địa bàn
9. **Mẫu 9**: Không có xe và chủ xe tại địa bàn
10. **Mẫu 10**: Xe không nằm trong danh sách

## 🔐 Bảo mật

### Thay đổi mật khẩu admin:

Sửa file `app/config.py`:

```python
ADMIN_USERNAME: str = "admin"
ADMIN_PASSWORD: str = "your_secure_password"  # Đổi mật khẩu này!
```

Hoặc tạo file `.env`:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

## 📊 Dữ liệu

Hệ thống hỗ trợ 2 nguồn dữ liệu:

### 1. File Excel Local (mặc định)
- Đọc từ thư mục `data/dulieuphuongtien/`
- Biển Xanh: ~300 bản ghi
- Biển Trắng/Vàng (40 sheets): Hàng chục nghìn bản ghi
- Yêu cầu lưu trong `requests/requests.json`

### 2. Google Sheets (khuyến nghị)
- ✅ Dữ liệu realtime, cập nhật trực tiếp
- ✅ Nhiều người cùng chỉnh sửa
- ✅ Tự động đồng bộ
- ✅ Yêu cầu tự động lưu vào Google Sheets

**Để sử dụng Google Sheets:**
1. Xem hướng dẫn chi tiết: [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)
2. Tạo Google Cloud Project và Service Account
3. Tạo 2 Google Sheets: "Dữ liệu Phương tiện" và "Yêu cầu Cập nhật"
4. Cấu hình file `.env` với Spreadsheet IDs
5. Restart server

## 🚀 Triển khai (Deployment)

### Chạy production với Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Deploy lên Heroku, Railway, hoặc VPS:

1. Cấu hình biến môi trường
2. Install dependencies
3. Chạy server với Gunicorn hoặc Uvicorn

## 📝 Ghi chú

- ✅ Hỗ trợ cả file Excel local VÀ Google Sheets
- ✅ Google Sheets API đã được tích hợp đầy đủ
- Yêu cầu lưu trong file JSON + Google Sheets (dual storage)
- Xem hướng dẫn setup Google Sheets tại: [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)

## 🤝 Hỗ trợ

Nếu gặp vấn đề khi cài đặt hoặc sử dụng, vui lòng kiểm tra:
- Python version >= 3.9
- Các dependencies đã cài đặt đầy đủ
- Đường dẫn file dữ liệu chính xác

## 📄 License

Dự án phục vụ cho UBND Phường Long Bình - 2025
