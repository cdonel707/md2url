from abc import ABC, abstractmethod
from typing import Tuple

class BaseReader(ABC):
    @abstractmethod
    async def read_url(self, url: str, inline_title: bool, ignore_links: bool) -> Tuple[str, str]:
        """
        Read and convert URL to markdown
        Returns: (markdown_content, page_title)
        """
        pass 