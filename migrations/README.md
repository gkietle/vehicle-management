# Database Migrations

## Overview
This folder contains database migration scripts for the vehicle management system.

## Migration: Add New Form Fields (2024-11-29)

### Purpose
Add new fields to the `requests` table to support updated forms 6-10 with additional information:
- Vehicle plate color (màu biển)
- Driver license (GPLX) information
- CCCD issue dates
- Transfer document status
- Seller and current user information (for form 10)

### Files
- `add_new_form_fields.sql` - PostgreSQL migration SQL
- `../run_migration.py` - Python migration script (works for both SQLite and PostgreSQL)

### How to Run

#### Automatic (Recommended)
Migrations run automatically on deployment via `start.sh`:
```bash
./start.sh
```

#### Manual - Local Development
```bash
python3 run_migration.py
```

#### Manual - Production (Railway)
The migration will run automatically on next deployment. If you need to run it manually:

**Option 1: Via Railway CLI**
```bash
railway run python3 run_migration.py
```

**Option 2: Via Railway Shell**
```bash
railway shell
python3 run_migration.py
exit
```

**Option 3: Direct SQL (PostgreSQL only)**
```bash
railway connect
\i migrations/add_new_form_fields.sql
\q
```

### Safety
- The migration script checks for existing columns before adding them
- Safe to run multiple times (idempotent)
- Works with both SQLite (local) and PostgreSQL (production)

### New Columns Added
1. `mau_bien` - License plate color
2. `ngay_cap_cccd_chu_xe` - Owner CCCD issue date
3. `so_gplx_chu_xe` - Owner driver license number
4. `ngay_cap_gplx_chu_xe` - Owner GPLX issue date
5. `co_quan_cap_gplx_chu_xe` - GPLX issuing authority
6. `ngay_cap_cccd_nguoi_mua` - Buyer/user CCCD issue date
7. `ban_sao_chuyen_nhuong` - Transfer document copy status
8. `ten_nguoi_dang_su_dung` - Current user name (form 10)
9. `dia_chi_nguoi_dang_su_dung` - Current user address (form 10)
10. `ten_nguoi_ban` - Seller name (form 10)
11. `dia_chi_nguoi_ban` - Seller address (form 10)
12. `so_dien_thoai_nguoi_ban` - Seller phone (form 10)
13. `so_cccd_nguoi_ban` - Seller CCCD (form 10)
14. `ngay_cap_cccd_nguoi_ban` - Seller CCCD issue date (form 10)

### Verification
After running migration, verify in database:

**PostgreSQL:**
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'requests'
ORDER BY ordinal_position;
```

**SQLite:**
```sql
PRAGMA table_info(requests);
```
