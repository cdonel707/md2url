import sys
import os

# Add your project directory to the sys.path
path = '/home/ChrisFern/md2url'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['PYTHONPATH'] = path

# Import the FastAPI app
from app.main import app

async def send(message):
    return message

# Create WSGI application
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    
    # Call the FastAPI app with the send function
    response = app(environ, start_response, send)
    return response