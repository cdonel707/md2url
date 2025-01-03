import sys
import os

# Add your project directory to the sys.path
path = '/home/ChrisFern/urltomarkdown'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['PYTHONPATH'] = path

from wsgi import application