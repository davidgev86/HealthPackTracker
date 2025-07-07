import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "hpm-inventory-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import routes after app creation to avoid circular imports
from routes import *

# Initialize CSV files if they don't exist
from utils import initialize_csv_files
initialize_csv_files()
