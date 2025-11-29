-- Migration: Add new fields to requests table for updated forms 6-10
-- Date: 2024-11-29

-- Add new columns to requests table
ALTER TABLE requests ADD COLUMN IF NOT EXISTS mau_bien VARCHAR(50);

-- GPLX and CCCD info for owner
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ngay_cap_cccd_chu_xe VARCHAR(50);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS so_gplx_chu_xe VARCHAR(100);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ngay_cap_gplx_chu_xe VARCHAR(50);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS co_quan_cap_gplx_chu_xe VARCHAR(200);

-- Buyer/transfer info updates
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ngay_cap_cccd_nguoi_mua VARCHAR(50);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ban_sao_chuyen_nhuong VARCHAR(50);

-- Form 10 specific fields (seller and current user info)
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ten_nguoi_dang_su_dung VARCHAR(200);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS dia_chi_nguoi_dang_su_dung TEXT;
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ten_nguoi_ban VARCHAR(200);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS dia_chi_nguoi_ban TEXT;
ALTER TABLE requests ADD COLUMN IF NOT EXISTS so_dien_thoai_nguoi_ban VARCHAR(50);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS so_cccd_nguoi_ban VARCHAR(50);
ALTER TABLE requests ADD COLUMN IF NOT EXISTS ngay_cap_cccd_nguoi_ban VARCHAR(50);

-- Create index on new searchable fields for performance
CREATE INDEX IF NOT EXISTS idx_requests_mau_bien ON requests(mau_bien);
CREATE INDEX IF NOT EXISTS idx_requests_so_gplx ON requests(so_gplx_chu_xe);

-- Verify migration
SELECT 'Migration completed successfully!' as status;
