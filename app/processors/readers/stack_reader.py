from typing import Tuple
from bs4 import BeautifulSoup
import aiohttp
from .base import BaseReader
from ..html_processor import process_html

class StackOverflowReader(BaseReader):
    async def read_url(self, url: str, inline_title: bool, ignore_links: bool) -> Tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError("Could not fetch StackOverflow page")
                html = await response.text()
                
                # Process question and answer separately
                soup = BeautifulSoup(html, 'html.parser')
                
                # Get question content
                question_div = soup.find('div', id='question')
                if not question_div:
                    raise ValueError("Could not find question content")
                
                question_md, title = process_html(str(question_div), url, inline_title, ignore_links)
                
                # Get accepted answer or highest voted answer
                answer_div = (
                    soup.find('div', attrs={'class': 'accepted-answer'}) or
                    soup.find('div', attrs={'class': 'answer'})
                )
                
                if answer_div:
                    answer_md, _ = process_html(str(answer_div), url, False, ignore_links)
                    return f"{question_md}\n\n## Answer\n\n{answer_md}", title
                
                return question_md, title 