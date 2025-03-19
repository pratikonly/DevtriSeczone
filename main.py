from flask import Flask, render_template, render_template_string
import os
import logging
import sys

# Configure logging to output to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    logger.info("Index route accessed")
    try:
        # Read the content from index.html
        with open('templates/index.html', 'r') as f:
            index_content = f.read()
            # Remove the extends and block tags
            index_content = index_content.replace('{% extends "base.html" %}', '')
            index_content = index_content.replace('{% block content %}', '')
            index_content = index_content.replace('{% endblock %}', '')

        # Render base.html with the index content
        return render_template('base.html', content_from_index_html=index_content)
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return "Internal Server Error", 500

@app.route('/ping')
def ping():
    logger.info("Ping endpoint called")
    return "pong", 200

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        sys.exit(1)