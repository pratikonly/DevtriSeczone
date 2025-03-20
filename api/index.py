from flask import Flask, render_template
import os

app = Flask(__name__, template_folder=os.path.abspath('../templates'))  # Ensure Flask finds templates

@app.route('/')
def home():
    return render_template('base.html')  # Renders base.html from templates folder

if __name__ == '__main__':
    app.run(debug=True)
