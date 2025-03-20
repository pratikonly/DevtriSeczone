import sqlite3
import logging
from app import app, db
from models import Visitor, ContactSubmission
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_visitor_data():
    """
    Migrate visitor data from local SQLite to PostgreSQL cloud database
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
        batch_size = 50
        offset = 0
        total_migrated = 0
        
        with app.app_context():
            while True:
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
                db.session.commit()
                total_migrated += len(batch)
                logger.info(f"Migrated batch of {len(batch)} visitors. Total: {total_migrated}/{count}")
                
                # Move to next batch
                offset += batch_size
                
            logger.info(f"Visitor data migration completed successfully. Total migrated: {total_migrated}")
    
    except Exception as e:
        logger.error(f"Error migrating visitor data: {str(e)}")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

def migrate_contact_submissions():
    """
    Migrate contact submissions from local SQLite to PostgreSQL cloud database
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
        batch_size = 20
        offset = 0
        total_migrated = 0
        
        with app.app_context():
            while True:
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
                db.session.commit()
                total_migrated += len(batch)
                logger.info(f"Migrated batch of {len(batch)} submissions. Total: {total_migrated}/{count}")
                
                # Move to next batch
                offset += batch_size
            
            logger.info(f"Contact submission data migration completed successfully. Total migrated: {total_migrated}")
    
    except Exception as e:
        logger.error(f"Error migrating contact submission data: {str(e)}")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == "__main__":
    logger.info("Starting data migration from SQLite to PostgreSQL...")
    migrate_visitor_data()
    migrate_contact_submissions()
    logger.info("Data migration complete!")