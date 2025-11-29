#!/usr/bin/env python3
"""
Migration script to add new fields to requests table
Run this script to apply database schema changes for updated forms 6-10
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text
from app.database import engine
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run database migration"""

    logger.info(f"Current DATABASE_URL: {settings.DATABASE_URL[:50]}...")

    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    logger.info(f"Database type: {'SQLite' if is_sqlite else 'PostgreSQL'}")

    # Define new columns to add
    new_columns = [
        ("batch_id", "INTEGER"),  # Link to batch
        ("mau_bien", "VARCHAR(50)"),
        ("ngay_cap_cccd_chu_xe", "VARCHAR(50)"),
        ("so_gplx_chu_xe", "VARCHAR(100)"),
        ("ngay_cap_gplx_chu_xe", "VARCHAR(50)"),
        ("co_quan_cap_gplx_chu_xe", "VARCHAR(200)"),
        ("ngay_cap_cccd_nguoi_mua", "VARCHAR(50)"),
        ("ban_sao_chuyen_nhuong", "VARCHAR(50)"),
        ("ten_nguoi_dang_su_dung", "VARCHAR(200)"),
        ("dia_chi_nguoi_dang_su_dung", "TEXT"),
        ("ten_nguoi_ban", "VARCHAR(200)"),
        ("dia_chi_nguoi_ban", "TEXT"),
        ("so_dien_thoai_nguoi_ban", "VARCHAR(50)"),
        ("so_cccd_nguoi_ban", "VARCHAR(50)"),
        ("ngay_cap_cccd_nguoi_ban", "VARCHAR(50)"),
    ]

    try:
        with engine.begin() as conn:
            logger.info("Starting migration...")

            # Get existing columns
            if is_sqlite:
                result = conn.execute(text("PRAGMA table_info(requests)"))
                existing_columns = {row[1] for row in result}
            else:
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'requests'
                """))
                existing_columns = {row[0] for row in result}

            logger.info(f"Found {len(existing_columns)} existing columns")

            # Add new columns
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    logger.info(f"Adding column: {col_name}")

                    if is_sqlite:
                        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
                        sql = f"ALTER TABLE requests ADD COLUMN {col_name} {col_type}"
                    else:
                        # PostgreSQL supports IF NOT EXISTS
                        sql = f"ALTER TABLE requests ADD COLUMN IF NOT EXISTS {col_name} {col_type}"

                    conn.execute(text(sql))
                else:
                    logger.info(f"Column {col_name} already exists, skipping")

            # Create indexes for PostgreSQL
            if not is_sqlite:
                logger.info("Creating indexes...")
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_requests_batch_id ON requests(batch_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_requests_mau_bien ON requests(mau_bien)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_requests_so_gplx ON requests(so_gplx_chu_xe)"))

                # Add foreign key constraint for batch_id (PostgreSQL only)
                logger.info("Adding foreign key constraint...")
                try:
                    conn.execute(text("""
                        ALTER TABLE requests
                        ADD CONSTRAINT fk_requests_batch_id
                        FOREIGN KEY (batch_id) REFERENCES batches(id)
                    """))
                except Exception as e:
                    logger.warning(f"Foreign key constraint may already exist: {e}")

            logger.info("✅ Migration completed successfully!")
            return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
