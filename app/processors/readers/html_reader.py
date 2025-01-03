from typing import Tuple
import aiohttp
from ..html_processor import process_html
from .base import BaseReader

class HTMLReader(BaseReader):
    async def read_url(self, url: str, inline_title: bool, ignore_links: bool) -> Tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError("Could not fetch URL")
                html = await response.text()
                return process_html(html, url, inline_title, ignore_links) 