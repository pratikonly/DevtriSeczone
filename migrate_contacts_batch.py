import sqlite3
import logging
import time
import sys
from app import app, db
from models import ContactSubmission
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_contacts_batch(start_offset, end_offset):
    """
    Migrate contact submissions from local SQLite to PostgreSQL cloud database
    within a specific batch range
    """
    try:
        # Connect to the SQLite database
        sqlite_conn = sqlite3.connect('instance/visitors.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        # Check if contact_submission table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_submission'")
        if not cursor.fetchone():
            logger.info("No contact_submission table found in SQLite database. Nothing to migrate.")
            return
        
        # Count submissions
        cursor.execute("SELECT COUNT(*) FROM contact_submission")
        count = cursor.fetchone()[0]
        if count == 0:
            logger.info("No contact submissions found in SQLite database. Nothing to migrate.")
            return
            
        logger.info(f"Found {count} contact submissions in SQLite database")
        
        # Process in batches to prevent timeout
        batch_size = 5
        offset = start_offset
        total_migrated = 0
        
        with app.app_context():
            while offset < end_offset:
                # Get a batch of submissions
                cursor.execute(f"SELECT * FROM contact_submission LIMIT {batch_size} OFFSET {offset}")
                batch = cursor.fetchall()
                
                if not batch:
                    break
                
                # Process this batch
                for submission_data in batch:
                    # Convert SQLite row to dict
                    submission_dict = dict(submission_data)
                    
                    # Convert timestamp string to datetime if needed
                    submission_time = submission_dict.get('submission_time')
                    if isinstance(submission_time, str):
                        try:
                            submission_time = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
                        except ValueError:
                            submission_time = datetime.utcnow()
                    
                    # Create new submission
                    new_submission = ContactSubmission(
                        name=submission_dict.get('name'),
                        email=submission_dict.get('email'),
                        message=submission_dict.get('message'),
                        submission_time=submission_time,
                        ip_address=submission_dict.get('ip_address'),
                        country=submission_dict.get('country'),
                        city=submission_dict.get('city'),
                        region=submission_dict.get('region')
                    )
                    db.session.add(new_submission)
                
                # Commit this batch
                try:
                    db.session.commit()
                    total_migrated += len(batch)
                    logger.info(f"Migrated batch of {len(batch)} submissions. Total: {total_migrated} (Offsets {offset}-{offset+len(batch)})")
                except Exception as batch_error:
                    db.session.rollback()
                    logger.error(f"Error committing batch at offset {offset}: {str(batch_error)}")
                
                # Move to next batch
                offset += batch_size
                
                # Add small pause to avoid overloading the database
                time.sleep(0.5)
            
            logger.info(f"Contact submission batch migration completed successfully. Total migrated: {total_migrated}")
    
    except Exception as e:
        logger.error(f"Error migrating contact submission data: {str(e)}")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == "__main__":
    # Get batch range from command line arguments
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
    
    logger.info(f"Starting contact submission migration for batch range {start}-{end}...")
    migrate_contacts_batch(start, end)
    logger.info(f"Contact submission batch migration complete for range {start}-{end}!")