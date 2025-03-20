import sqlite3
import logging
import time
import sys
from app import app, db
from models import Visitor
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_visitor_batch(start_offset, end_offset):
    """
    Migrate visitor data from local SQLite to PostgreSQL cloud database
    within a specific batch range
    """
    try:
        # Connect to the SQLite database
        sqlite_conn = sqlite3.connect('instance/visitors.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        # Check if visitors table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visitor'")
        if not cursor.fetchone():
            logger.info("No visitors table found in SQLite database. Nothing to migrate.")
            return
        
        # Count visitors
        cursor.execute("SELECT COUNT(*) FROM visitor")
        count = cursor.fetchone()[0]
        logger.info(f"Found {count} visitors in SQLite database")
        
        # Process in batches to prevent timeout
        batch_size = 10
        offset = start_offset
        total_migrated = 0
        
        with app.app_context():
            while offset < end_offset:
                # Get a batch of visitors
                cursor.execute(f"SELECT * FROM visitor LIMIT {batch_size} OFFSET {offset}")
                batch = cursor.fetchall()
                
                if not batch:
                    break
                
                # Process this batch
                for visitor_data in batch:
                    # Convert SQLite row to dict
                    visitor_dict = dict(visitor_data)
                    
                    # Convert timestamp string to datetime if needed
                    visit_time = visitor_dict.get('visit_time')
                    if isinstance(visit_time, str):
                        try:
                            visit_time = datetime.fromisoformat(visit_time.replace('Z', '+00:00'))
                        except ValueError:
                            visit_time = datetime.utcnow()
                    
                    # Create new visitor
                    new_visitor = Visitor(
                        ip_address=visitor_dict.get('ip_address'),
                        visit_time=visit_time,
                        country=visitor_dict.get('country'),
                        city=visitor_dict.get('city'),
                        region=visitor_dict.get('region')
                    )
                    db.session.add(new_visitor)
                
                # Commit this batch
                try:
                    db.session.commit()
                    total_migrated += len(batch)
                    logger.info(f"Migrated batch of {len(batch)} visitors. Total: {total_migrated} (Offsets {offset}-{offset+len(batch)})")
                except Exception as batch_error:
                    db.session.rollback()
                    logger.error(f"Error committing batch at offset {offset}: {str(batch_error)}")
                
                # Move to next batch
                offset += batch_size
                
                # Add small pause to avoid overloading the database
                time.sleep(0.5)
                
            logger.info(f"Visitor data batch migration completed successfully. Total migrated: {total_migrated}")
    
    except Exception as e:
        logger.error(f"Error migrating visitor data: {str(e)}")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == "__main__":
    # Get batch range from command line arguments
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
    
    logger.info(f"Starting visitor data migration for batch range {start}-{end}...")
    migrate_visitor_batch(start, end)
    logger.info(f"Visitor data batch migration complete for range {start}-{end}!")