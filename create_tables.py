import logging
import os
import psycopg2
from app import app, db
from models import Visitor, ContactSubmission

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """
    Create all tables in the database
    """
    try:
        logger.info("Creating all database tables...")
        # Try ORM approach first
        with app.app_context():
            db.create_all()
            logger.info("ORM tables creation attempted")
        
        # Also use SQL directly to ensure tables exist
        conn = None
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            cursor = conn.cursor()
            
            # Create visitor table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitor (
                id SERIAL PRIMARY KEY,
                ip_address VARCHAR(50) NOT NULL,
                visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                country VARCHAR(100),
                city VARCHAR(100),
                region VARCHAR(100)
            )
            """)
            
            # Create contact_submission table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_submission (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL,
                message TEXT NOT NULL,
                submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                country VARCHAR(100),
                city VARCHAR(100),
                region VARCHAR(100)
            )
            """)
            
            conn.commit()
            logger.info("SQL tables creation completed")
            
            # Verify tables exist
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            logger.info(f"Tables in database: {table_names}")
            
        except Exception as e:
            logger.error(f"Error in SQL table creation: {str(e)}")
        finally:
            if conn is not None:
                conn.close()
        
        # Verify tables through ORM
        with app.app_context():
            try:
                visitor_count = db.session.execute(db.select(Visitor).limit(1)).all()
                logger.info(f"Visitor table accessible through ORM: {len(visitor_count) >= 0}")
            except Exception as e:
                logger.error(f"Error checking Visitor table via ORM: {str(e)}")
            
            try:
                contact_count = db.session.execute(db.select(ContactSubmission).limit(1)).all()
                logger.info(f"ContactSubmission table accessible through ORM: {len(contact_count) >= 0}")
            except Exception as e:
                logger.error(f"Error checking ContactSubmission table via ORM: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    create_all_tables()