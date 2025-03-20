import os
import logging
import requests
from flask import render_template, request, flash, redirect, url_for
from email_validator import validate_email, EmailNotValidError
from app import app, db
from models import Visitor, ContactSubmission

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure the static/images directory exists
images_dir = os.path.join(app.static_folder, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    logger.info(f"Created images directory at {images_dir}")

@app.route('/')
def index():
    logger.debug("Rendering index page")
    total_visitors = Visitor.query.count()
    current_visitor = None
    
    try:
        client_ip = request.remote_addr
        new_visitor = Visitor(ip_address=client_ip)

        try:
            response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"IP API response: {data}")
                new_visitor.country = data.get('country', 'Unknown')
                new_visitor.city = data.get('city', 'Unknown')
                new_visitor.region = data.get('regionName', 'Unknown')
        except Exception as e:
            logger.error(f"Error fetching location data: {str(e)}")

        db.session.add(new_visitor)
        db.session.commit()
        
        # Set the current visitor for display
        current_visitor = new_visitor
    except Exception as e:
        logger.error(f"Error recording visitor: {str(e)}")

    return render_template('index.html', total_visitors=total_visitors, current_visitor=current_visitor)

@app.route('/flash-news')
def flash_news():
    return render_template('flash_news.html')

@app.route('/visitor-stats')
def visitor_stats():
    # Get visitors in reverse chronological order (newest first)
    visitors = Visitor.query.order_by(Visitor.visit_time.desc()).all()
    total_visitors = len(visitors)
    
    # Get statistics by country
    country_stats = {}
    for visitor in visitors:
        country = visitor.country or 'Unknown'
        if country in country_stats:
            country_stats[country] += 1
        else:
            country_stats[country] = 1
    
    return render_template('visitor_stats.html', 
                          total_visitors=total_visitors, 
                          visitors=visitors,
                          country_stats=country_stats)

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

        # Create a new contact submission record
        client_ip = request.remote_addr
        new_submission = ContactSubmission(
            name=name,
            email=email,
            message=message,
            ip_address=client_ip
        )
        
        # Try to get location data for the submission
        try:
            response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"IP API response for contact form: {data}")
                new_submission.country = data.get('country', 'Unknown')
                new_submission.city = data.get('city', 'Unknown')
                new_submission.region = data.get('regionName', 'Unknown')
        except Exception as e:
            logger.error(f"Error fetching location data for contact form: {str(e)}")
        
        # Save to the database
        db.session.add(new_submission)
        db.session.commit()
        logger.info(f"Saved contact submission from {name} <{email}> to database")
        
        # In a real implementation, you would also send the email here
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('index', _anchor='contact'))

    except Exception as e:
        logger.error(f"Error in contact form: {str(e)}")
        flash('An error occurred. Please try again later.', 'error')
        return redirect(url_for('index', _anchor='contact'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)