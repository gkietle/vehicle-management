"""
Migration script to add indexes for performance optimization
"""
from app.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_indexes():
    """Add indexes to vehicle_records table for search performance"""

    with engine.connect() as conn:
        try:
            # Check if indexes already exist
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
            existing_indexes = [row[0] for row in result]

            logger.info(f"Existing indexes: {existing_indexes}")

            # Add index for so_khung
            if 'ix_vehicle_records_so_khung' not in existing_indexes:
                logger.info("Creating index on so_khung...")
                conn.execute(text("CREATE INDEX ix_vehicle_records_so_khung ON vehicle_records (so_khung)"))
                conn.commit()
                logger.info("✓ Created index on so_khung")
            else:
                logger.info("Index on so_khung already exists")

            # Add index for so_may
            if 'ix_vehicle_records_so_may' not in existing_indexes:
                logger.info("Creating index on so_may...")
                conn.execute(text("CREATE INDEX ix_vehicle_records_so_may ON vehicle_records (so_may)"))
                conn.commit()
                logger.info("✓ Created index on so_may")
            else:
                logger.info("Index on so_may already exists")

            # Add index for so_dien_thoai
            if 'ix_vehicle_records_so_dien_thoai' not in existing_indexes:
                logger.info("Creating index on so_dien_thoai...")
                conn.execute(text("CREATE INDEX ix_vehicle_records_so_dien_thoai ON vehicle_records (so_dien_thoai)"))
                conn.commit()
                logger.info("✓ Created index on so_dien_thoai")
            else:
                logger.info("Index on so_dien_thoai already exists")

            logger.info("✓ All indexes created successfully!")

            # Show all indexes now
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='vehicle_records'"))
            all_indexes = [row[0] for row in result]
            logger.info(f"All indexes on vehicle_records: {all_indexes}")

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise


if __name__ == "__main__":
    logger.info("Starting index creation...")
    add_indexes()
    logger.info("Done!")
