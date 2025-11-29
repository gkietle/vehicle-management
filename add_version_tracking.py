#!/usr/bin/env python3
"""
Migration script to add version tracking to requests table
Adds: version, is_latest_approved columns
"""

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Add version tracking columns to requests table"""

    # Create engine
    engine = create_engine(settings.DATABASE_URL)

    # Detect database type
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")

    logger.info(f"Running migration on {'SQLite' if is_sqlite else 'PostgreSQL'}")

    with engine.connect() as conn:
        # Check if columns exist
        if is_sqlite:
            result = conn.execute(text("PRAGMA table_info(requests)"))
            existing_columns = {row[1] for row in result}
        else:
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'requests'
            """))
            existing_columns = {row[0] for row in result}

        logger.info(f"Found {len(existing_columns)} existing columns")

        # Add version column
        if "version" not in existing_columns:
            logger.info("Adding 'version' column...")
            if is_sqlite:
                conn.execute(text("ALTER TABLE requests ADD COLUMN version INTEGER DEFAULT 1"))
            else:
                conn.execute(text("ALTER TABLE requests ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1"))

            # Create index
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_requests_version ON requests(version)"))
            except Exception as e:
                logger.warning(f"Could not create index on version: {e}")

            logger.info("✓ Added 'version' column")
        else:
            logger.info("✓ 'version' column already exists")

        # Add is_latest_approved column
        if "is_latest_approved" not in existing_columns:
            logger.info("Adding 'is_latest_approved' column...")
            if is_sqlite:
                conn.execute(text("ALTER TABLE requests ADD COLUMN is_latest_approved INTEGER DEFAULT 0"))
            else:
                conn.execute(text("ALTER TABLE requests ADD COLUMN IF NOT EXISTS is_latest_approved BOOLEAN DEFAULT FALSE"))

            # Create index
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_requests_is_latest_approved ON requests(is_latest_approved)"))
            except Exception as e:
                logger.warning(f"Could not create index on is_latest_approved: {e}")

            logger.info("✓ Added 'is_latest_approved' column")
        else:
            logger.info("✓ 'is_latest_approved' column already exists")

        # Update existing requests to version 1
        logger.info("Setting version=1 for existing requests...")
        conn.execute(text("UPDATE requests SET version = 1 WHERE version IS NULL"))

        # Mark latest approved requests
        logger.info("Marking latest approved requests...")
        if is_sqlite:
            # SQLite compatible query
            conn.execute(text("""
                UPDATE requests
                SET is_latest_approved = 1
                WHERE trang_thai = 'approved'
                AND id IN (
                    SELECT r1.id
                    FROM requests r1
                    LEFT JOIN requests r2
                      ON r1.bien_so = r2.bien_so
                      AND r1.loai_mau = r2.loai_mau
                      AND r1.ngay_tao < r2.ngay_tao
                      AND r2.trang_thai = 'approved'
                    WHERE r2.id IS NULL
                )
            """))
        else:
            # PostgreSQL compatible query
            conn.execute(text("""
                UPDATE requests r1
                SET is_latest_approved = TRUE
                WHERE r1.trang_thai = 'approved'
                AND NOT EXISTS (
                    SELECT 1 FROM requests r2
                    WHERE r2.bien_so = r1.bien_so
                    AND r2.loai_mau = r1.loai_mau
                    AND r2.trang_thai = 'approved'
                    AND r2.ngay_tao > r1.ngay_tao
                )
            """))

        conn.commit()
        logger.info("✓ Migration completed successfully")


if __name__ == "__main__":
    try:
        run_migration()
        print("\n✅ Version tracking migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
