# Hướng dẫn Deploy lên Railway

## 📋 Yêu cầu
- Tài khoản GitHub
- Tài khoản Railway (free tier)

## 🚀 Các bước deploy

### 1. Push code lên GitHub

```bash
# Khởi tạo git repository (nếu chưa có)
git init

# Add tất cả files
git add .

# Commit
git commit -m "Initial commit - Ready for deployment"

# Tạo repository trên GitHub và push
git remote add origin https://github.com/YOUR_USERNAME/vehicle-management.git
git branch -M main
git push -u origin main
```

### 2. Deploy trên Railway

1. Truy cập [Railway.app](https://railway.app)
2. Đăng nhập bằng GitHub
3. Click "New Project"
4. Chọn "Deploy from GitHub repo"
5. Chọn repository `vehicle-management`
6. Railway sẽ tự động detect Dockerfile và bắt đầu build

### 3. Add PostgreSQL Database

1. Trong project dashboard, click "New"
2. Chọn "Database" → "Add PostgreSQL"
3. Railway sẽ tự động tạo database và set biến `DATABASE_URL`

### 4. Configure Environment Variables

Trong tab "Variables", thêm các biến sau:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
```

**Lưu ý:** Railway tự động set `DATABASE_URL` và `PORT`, không cần thêm thủ công.

### 5. Deploy

1. Railway sẽ tự động build và deploy
2. Sau khi deploy xong, click vào "Generate Domain" để có public URL
3. Truy cập URL để kiểm tra: `https://your-app.up.railway.app`

### 6. Upload dữ liệu

1. Truy cập `/admin/batches` (đăng nhập bằng admin credentials)
2. Tạo batch mới (ví dụ: "UAT Data - Tháng 11/2024")
3. Upload các file Excel vào batch
4. Click "Kích hoạt" để set batch làm active
5. Dữ liệu sẽ tự động được import vào PostgreSQL

## 🔄 Auto-deploy khi có thay đổi

Railway tự động deploy lại khi bạn push code mới lên GitHub:

```bash
git add .
git commit -m "Your changes"
git push
```

Railway sẽ tự động detect và deploy version mới.

## 📊 Monitoring

- **Logs**: Xem trong tab "Deployments" → Click vào deployment → "View Logs"
- **Metrics**: Tab "Metrics" hiện CPU, Memory, Network usage
- **Database**: Tab "Data" để xem PostgreSQL metrics

## 🧪 Test local với Docker

Trước khi deploy, test local:

```bash
# Build và chạy với docker-compose
docker-compose up --build

# Truy cập http://localhost:8000
```

## 🛠️ Troubleshooting

### App không start
- Check logs trong Railway dashboard
- Verify environment variables đã set đúng
- Ensure PostgreSQL database đã được tạo

### Database connection error
- Kiểm tra biến `DATABASE_URL` có được set tự động không
- Ensure PostgreSQL service đang chạy

### File upload không hoạt động
- Kiểm tra folder `data/batches` có được tạo
- Check logs để xem lỗi cụ thể

## 💰 Free Tier Limits

Railway free tier includes:
- 500 hours/month runtime
- $5 credit/month
- Đủ cho UAT nhỏ với < 100 users concurrent

## 📝 Notes

- Database được persist, không mất data khi redeploy
- Uploaded files lưu trong container, sẽ mất khi redeploy. Nên backup database thường xuyên.
- Để production, nên upgrade plan và setup volume storage cho files.
