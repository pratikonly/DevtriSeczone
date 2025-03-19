import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from email_validator import validate_email, EmailNotValidError
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
db.init_app(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Ensure the static/images directory exists
images_dir = os.path.join(app.static_folder, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    logger.info(f"Created images directory at {images_dir}")

@app.route('/')
def index():
    logger.debug("Rendering index page")
    client_ip = request.remote_addr
    new_visitor = Visitor(ip_address=client_ip)
    db.session.add(new_visitor)
    db.session.commit()
    return render_template('index.html')

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
    app.run(host='0.0.0.0', port=5000, debug=True)