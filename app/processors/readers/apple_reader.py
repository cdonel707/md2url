from typing import Tuple, Dict, Any
import json
import aiohttp
from urllib.parse import urlparse
from .base import BaseReader

class AppleReader(BaseReader):
    async def read_url(self, url: str, inline_title: bool, ignore_links: bool) -> Tuple[str, str]:
        json_url = self._get_json_url(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(json_url) as response:
                if response.status != 200:
                    raise ValueError("Could not fetch Apple documentation")
                data = await response.json()
                return self._parse_doc_json(data, inline_title, ignore_links)

    def _get_json_url(self, url: str) -> str:
        """Convert Apple doc URL to JSON API URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # Build JSON API URL
        json_url = "https://developer.apple.com/tutorials/data"
        for part in path_parts[1:]:  # Skip first part after domain
            json_url += f"/{part}"
        json_url += ".json"
        
        return json_url

    def _parse_doc_json(self, data: Dict[Any, Any], inline_title: bool, ignore_links: bool) -> Tuple[str, str]:
        """Parse Apple documentation JSON into markdown"""
        title = data.get('metadata', {}).get('title', '')
        content = []

        if inline_title and title:
            content.append(f"# {title}\n")

        # Process main content sections
        sections = data.get('primaryContentSections', data.get('sections', []))
        for section in sections:
            content.extend(self._process_section(section, ignore_links))

        return '\n'.join(content), title

    def _process_section(self, section: Dict[Any, Any], ignore_links: bool) -> list:
        """Process a single documentation section"""
        content = []
        
        # Handle declarations
        if section.get('kind') == 'declarations':
            for decl in section.get('declarations', []):
                content.extend(self._process_declaration(decl))
        
        # Handle content sections
        for content_section in section.get('content', []):
            content.extend(self._process_content(content_section, ignore_links))
        
        return content

    def _process_declaration(self, declaration: Dict[Any, Any]) -> list:
        """Process a declaration section"""
        content = []
        
        if 'tokens' in declaration:
            tokens = []
            for token in declaration['tokens']:
                tokens.append(token.get('text', ''))
            content.append('```\n' + ''.join(tokens) + '\n```\n')
        
        return content

    def _process_content(self, content: Dict[Any, Any], ignore_links: bool) -> list:
        """Process a content section"""
        result = []
        
        content_type = content.get('type', '')
        
        if content_type == 'text':
            if 'inlineContent' in content:
                inline_text = []
                for inline in content['inlineContent']:
                    inline_text.append(self._process_inline_content(inline, ignore_links))
                result.append(''.join(inline_text) + '\n')
        
        elif content_type == 'codeListing':
            if 'code' in content:
                result.append('```\n' + '\n'.join(content['code']) + '\n```\n')
        
        elif content_type in ['unorderedList', 'orderedList']:
            for idx, item in enumerate(content.get('items', []), 1):
                prefix = '* ' if content_type == 'unorderedList' else f'{idx}. '
                item_content = self._process_content(item, ignore_links)
                result.extend(prefix + line for line in item_content)
        
        elif content_type == 'heading':
            level = content.get('level', 1)
            text = content.get('text', '')
            result.append(f"{'#' * level} {text}\n")
        
        return result

    def _process_inline_content(self, inline: Dict[Any, Any], ignore_links: bool) -> str:
        """Process inline content elements"""
        if inline.get('type') == 'text':
            return inline.get('text', '')
        
        elif inline.get('type') == 'link' and not ignore_links:
            return f"[{inline.get('title', '')}]({inline.get('destination', '')})"
        
        elif inline.get('type') == 'link' and ignore_links:
            return inline.get('title', '')
        
        elif inline.get('type') == 'codeVoice':
            return f"`{inline.get('code', '')}`"
        
        return '' 