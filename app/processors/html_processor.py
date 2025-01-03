from typing import Tuple
from bs4 import BeautifulSoup
from readability import Document
import html2text
from .formatters import format_tables, format_code_blocks
from .filters import apply_filters

def process_html(html: str, url: str = None, inline_title: bool = False, ignore_links: bool = False) -> Tuple[str, str]:
    """Process HTML content and return markdown and title"""
    
    # Parse with readability
    doc = Document(html)
    title = doc.title()
    content = doc.summary()
    
    # Format special elements
    content = format_tables(content)
    content = format_code_blocks(content)
    
    # Convert to markdown
    h = html2text.HTML2Text()
    h.body_width = 0  # No wrapping
    h.ignore_links = ignore_links
    markdown = h.handle(content)
    
    # Apply filters
    if url:
        markdown = apply_filters(url, markdown)
    
    # Add title if requested
    if inline_title and title:
        markdown = f"# {title}\n\n{markdown}"
    
    return markdown, title 