# Railway Deploy - Hướng dẫn chi tiết từng bước

## Bước 1: Deploy ứng dụng từ GitHub

1. Truy cập https://railway.app và đăng nhập
2. Click **"New Project"**
3. Chọn **"Deploy from GitHub repo"**
4. Authorize Railway truy cập GitHub nếu chưa
5. Chọn repository của bạn
6. Railway sẽ tự động:
   - Detect Dockerfile
   - Bắt đầu build
   - Deploy lần đầu (SẼ LỖI vì chưa có database - đây là bình thường!)

## Bước 2: Add PostgreSQL Database

Sau khi deploy lần đầu (dù có lỗi):

1. Trong project dashboard, bạn sẽ thấy service vừa deploy
2. Click vào **"+ New"** button (góc trên phải)
3. Chọn **"Database"**
4. Chọn **"Add PostgreSQL"**
5. Railway sẽ tự động:
   - Tạo PostgreSQL instance
   - Link database với service của bạn
   - Tự động add biến `DATABASE_URL` vào service

## Bước 3: Set Environment Variables

1. Click vào **service name** (web app) trong dashboard
2. Chọn tab **"Variables"**
3. Click **"+ New Variable"**
4. Add từng biến:
   ```
   ADMIN_USERNAME = admin
   ADMIN_PASSWORD = your_password_here
   ```
5. Click **"Add"** sau mỗi biến

**LƯU Ý**: Biến `DATABASE_URL` và `PORT` đã được Railway tự động set, KHÔNG cần add thủ công!

## Bước 4: Redeploy

Sau khi add database và environment variables:

1. Vào tab **"Deployments"**
2. Click **"Deploy"** button (hoặc Railway sẽ tự động redeploy)
3. Xem logs để theo dõi quá trình deploy:
   ```
   Starting Vehicle Management System...
   Waiting for PostgreSQL to be ready...
   PostgreSQL is ready!
   Initializing database...
   Starting web server...
   ```

## Bước 5: Generate Domain (Public URL)

1. Vào tab **"Settings"**
2. Scroll xuống phần **"Networking"**
3. Click **"Generate Domain"**
4. Railway sẽ tạo URL dạng: `https://your-app-name.up.railway.app`
5. Copy URL này để truy cập app

## Bước 6: Kiểm tra

Truy cập các URLs sau:

- `https://your-app.up.railway.app` - Trang chủ
- `https://your-app.up.railway.app/health` - Health check
- `https://your-app.up.railway.app/admin/dashboard` - Admin dashboard (dùng credentials đã set)

## Debug khi có lỗi

### Xem logs:
1. Click vào service name
2. Tab **"Deployments"**
3. Click vào deployment mới nhất
4. Tab **"View Logs"**

### Các lỗi thường gặp:

#### 1. "Application failed to respond"
- **Nguyên nhân**: Database chưa connect hoặc port sai
- **Giải pháp**: 
  - Verify `DATABASE_URL` đã được set (tab Variables)
  - Check logs xem database có connect được không

#### 2. "ModuleNotFoundError: No module named 'psycopg2'"
- **Nguyên nhân**: requirements.txt không đúng
- **Giải pháp**: Push lại với requirements.txt đã update

#### 3. Database connection timeout
- **Nguyên nhân**: PostgreSQL chưa sẵn sàng
- **Giải pháp**: start.sh đã có logic wait, nhưng có thể cần tăng timeout

### Verify biến môi trường:

Trong tab **Variables**, bạn nên thấy:
```
DATABASE_URL          postgresql://postgres:...@...railway.app:5432/railway
PORT                  [auto-set by Railway]
ADMIN_USERNAME        admin
ADMIN_PASSWORD        your_password
```

## Tips

- **Auto-redeploy**: Mỗi lần push code mới lên GitHub, Railway tự động deploy
- **Database persistence**: Data trong PostgreSQL không mất khi redeploy
- **Logs realtime**: Xem logs trực tiếp khi app đang chạy
- **Resource usage**: Tab "Metrics" để xem CPU/Memory/Network

## Checklist hoàn thành

- [ ] App service đã được tạo từ GitHub
- [ ] PostgreSQL database đã được add
- [ ] DATABASE_URL đã tự động được set
- [ ] ADMIN_USERNAME và ADMIN_PASSWORD đã được set
- [ ] Deploy thành công (check logs)
- [ ] Domain đã được generate
- [ ] Health check endpoint trả về OK
- [ ] Đăng nhập admin dashboard được
- [ ] Upload file Excel vào batch thành công
