from .base import BaseReader
from .html_reader import HTMLReader
from .apple_reader import AppleReader
from .stack_reader import StackOverflowReader

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
