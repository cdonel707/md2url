import aiohttp
from bs4 import BeautifulSoup
import html2text
from readability import Document
import re

class URLReader:
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.body_width = 0
        self.html2text.ignore_images = True
        self.html2text.skip_internal_links = False
        self.html2text.links_each_paragraph = True

    async def read_url(self, url: str, include_title: bool = False, remove_links: bool = False) -> tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        # Use readability to extract main content
        doc = Document(html)
        title = doc.title()
        content = doc.summary()

        # Configure HTML2Text
        self.html2text.ignore_links = remove_links

        # Convert to markdown
        markdown = self.html2text.handle(content)

        # Add title if requested
        if include_title and title:
            markdown = f"# {title}\n\n{markdown}"

        return markdown, title

def get_reader_for_url(url: str) -> URLReader:
    """Factory function to get the appropriate reader for a URL"""
    return URLReader() 