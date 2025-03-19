import os
import logging
import requests
from flask import Flask, render_template, request, flash, redirect, url_for
from email_validator import validate_email, EmailNotValidError
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the PostgreSQL database with fallback
db_uri = os.environ.get("DATABASE_URL")
if not db_uri:
    logger.warning("DATABASE_URL not set, falling back to SQLite")
    db_uri = 'sqlite:///visitors.db'

logger.info(f"Configuring database with URI type: {'PostgreSQL' if 'postgresql' in db_uri else 'SQLite'}")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))

# Create tables
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

# Ensure the static/images directory exists
images_dir = os.path.join(app.static_folder, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    logger.info(f"Created images directory at {images_dir}")

@app.route('/')
def index():
    logger.debug("Starting index route handler")
    try:
        # Get all visitors for stats
        visitors = Visitor.query.order_by(Visitor.visit_time.desc()).all()
        total_visitors = len(visitors)
        logger.info(f"Retrieved {total_visitors} visitors from database")

        # Record new visitor
        client_ip = request.remote_addr
        new_visitor = Visitor(ip_address=client_ip)

        try:
            response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                new_visitor.country = data.get('country', 'Unknown')
                new_visitor.city = data.get('city', 'Unknown')
                new_visitor.region = data.get('regionName', 'Unknown')
                logger.debug(f"Retrieved location data for IP: {client_ip}")
        except Exception as e:
            logger.error(f"Error fetching location data: {str(e)}")

        db.session.add(new_visitor)
        db.session.commit()
        logger.info(f"New visitor recorded: {client_ip}")

        return render_template('index.html', total_visitors=total_visitors, visitors=visitors)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return "An error occurred. Please try again later.", 500

@app.route('/flash-news')
def flash_news():
    logger.debug("Rendering flash news page")
    return render_template('flash_news.html')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not all([name, email, message]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('index', _anchor='contact'))

        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('index', _anchor='contact'))

        # In a real implementation, you would send the email here
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('index', _anchor='contact'))

    except Exception as e:
        logger.error(f"Error in contact form: {str(e)}")
        flash('An error occurred. Please try again later.', 'error')
        return redirect(url_for('index', _anchor='contact'))

if __name__ == '__main__':
    logger.info("Starting Flask application on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)