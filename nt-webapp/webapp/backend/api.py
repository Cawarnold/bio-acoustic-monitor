import time
from flask import Flask
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for all routes

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}