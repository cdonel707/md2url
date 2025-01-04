from typing import Tuple
import aiohttp
from bs4 import BeautifulSoup
import html2text
from readability import Document
from .base import BaseReader

class HTMLReader(BaseReader):
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.body_width = 0
        self.html2text.ignore_images = True
        self.html2text.skip_internal_links = True
        self.html2text.links_each_paragraph = True

    async def read_url(self, url: str, include_title: bool = False, remove_links: bool = False) -> tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        # Use readability to extract main content
        doc = Document(html)
        title = doc.title()
        content = doc.summary()

        # Remove reference links using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        for a in soup.find_all('a', href=True):
            if '/reference' in a['href'] or '/ref' in a['href']:
                # Replace link with just its text content
                a.replace_with(a.get_text())
        
        # Get the modified HTML
        content = str(soup)

        # Configure HTML2Text
        self.html2text.ignore_links = remove_links

        # Convert to markdown
        markdown = self.html2text.handle(content)

        # Add title if requested
        if include_title and title:
            markdown = f"# {title}\n\n{markdown}"

        return markdown, title 

    def extract_links(self, markdown: str) -> list[str]:
        """Extract all URLs from markdown content"""
        import re
        # Match markdown links [text](url) and bare URLs
        url_pattern = r'\[([^\]]+)\]\(([^)]+)\)|(?:^|\s)(https?://[^\s<]+[\w#/])'
        links = []
        
        for match in re.finditer(url_pattern, markdown):
            if match.group(2):  # Markdown link
                links.append(match.group(2))
            elif match.group(3):  # Bare URL
                links.append(match.group(3))
        
        return links 