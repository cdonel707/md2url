import re
from urllib.parse import urlparse
from typing import List, Dict, Pattern, Union

class ContentFilter:
    def __init__(self):
        self.filters = [
            {
                'domain': re.compile(r'.*'),
                'remove': [
                    re.compile(r'\[¶\]\(#[^\s]+\s+"[^"]+"\)'),
                ],
                'replace': [
                    {
                        'find': re.compile(r'\[([^\]]*)\]\(\/\/([^\)]*)\)'),
                        'replacement': r'[\1](https://\2)'
                    }
                ]
            },
            {
                'domain': re.compile(r'.*\.wikipedia\.org'),
                'remove': [
                    re.compile(r'\*\*\[\^\]\(#cite_ref[^\)]+\)\*\*'),
                    re.compile(r'(?:\\\[)?\[edit\]\([^\s]+\s+"[^"]+"\)(?:\\\])?', re.I),
                    re.compile(r'\^\s\[Jump up to[^\)]*\)', re.I),
                    re.compile(r'\[[^\]]*\]\(#cite_ref[^\)]+\)'),
                    re.compile(r'\[\!\[Edit this at Wikidata\].*'),
                ],
                'replace': [
                    {
                        'find': re.compile(r'\(https:\/\/upload\.wikimedia\.org\/wikipedia\/([^\/]+)\/thumb\/([^\)]+\..{3,4})\/[^\)]+\)', re.I),
                        'replacement': r'(https://upload.wikimedia.org/wikipedia/\1/\2)'
                    }
                ]
            },
            {
                'domain': re.compile(r'(?:.*\.)?medium\.com'),
                'replace': [
                    {
                        'find': '(https://miro.medium.com/max/60/',
                        'replacement': '(https://miro.medium.com/max/600/'
                    }
                ]
            }
        ]

    def apply_filters(self, url: str, content: str, ignore_links: bool = False) -> str:
        """Apply filters based on URL domain"""
        if not url:
            return content

        domain = urlparse(url).netloc
        
        for filter_set in self.filters:
            if filter_set['domain'].match(domain):
                # Apply removals
                if 'remove' in filter_set:
                    for pattern in filter_set['remove']:
                        content = pattern.sub('', content)
                
                # Apply replacements
                if 'replace' in filter_set:
                    for replacement in filter_set['replace']:
                        content = replacement['find'].sub(replacement['replacement'], content)

        # Handle relative URLs
        base_url = f"{urlparse(url).scheme}://{domain}"
        content = re.sub(
            r'\[([^\]]*)\]\(\/([^\/][^\)]*)\)',
            rf'[\1]({base_url}/\2)',
            content
        )

        # Remove inline links if requested
        if ignore_links:
            content = re.sub(r'\[\[?([^\]]+\]?)\]\([^\)]+\)', r'\1', content)
            content = re.sub(r'[\\\[]+([0-9]+)[\\\]]+', r'[\1]', content)

        return content

# Create singleton instance
content_filter = ContentFilter()

def apply_filters(url: str, content: str, ignore_links: bool = False) -> str:
    """Apply content filters to markdown"""
    return content_filter.apply_filters(url, content, ignore_links) 