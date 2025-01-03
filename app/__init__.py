from app.processors.readers.base import BaseReader
from app.processors.readers.html_reader import HTMLReader
from app.processors.readers.apple_reader import AppleReader
from app.processors.readers.stack_reader import StackOverflowReader

def get_reader_for_url(url: str):
    """Factory function to get appropriate reader for URL"""
    from urllib.parse import urlparse
    
    domain = urlparse(url).netloc
    
    if domain == 'developer.apple.com':
        return AppleReader()
    elif domain == 'stackoverflow.com':
        return StackOverflowReader()
    else:
        return HTMLReader() 