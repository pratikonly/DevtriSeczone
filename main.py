import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
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
        
        # In a real implementation, you would send the email here
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('index', _anchor='contact'))
        
    except Exception as e:
        logging.error(f"Error in contact form: {str(e)}")
        flash('An error occurred. Please try again later.', 'error')
        return redirect(url_for('index', _anchor='contact'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
