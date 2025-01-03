from bs4 import BeautifulSoup
import re
from typing import List, Dict
import html

class TableFormatter:
    def __init__(self, max_width: int = 96):
        self.max_width = max_width

    def format_cell(self, cell: str, width: int) -> str:
        """Format and pad cell content"""
        cell = cell.strip()
        return cell.ljust(width)

    def convert_table(self, table_html: str) -> str:
        soup = BeautifulSoup(table_html, 'html.parser')
        
        # Extract caption if present
        caption = soup.find('caption')
        result = '\n'
        if caption:
            result += f"{caption.get_text().strip()}\n\n"

        # Collect rows and cells
        rows = []
        for tr in soup.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                text = td.get_text().strip()
                text = re.sub(r'\s+', ' ', text)
                cells.append(text)
            rows.append(cells)

        if not rows or len(rows) < 2:
            return ""

        # Calculate column widths
        col_widths = []
        for row in rows:
            while len(col_widths) < len(row):
                col_widths.append(3)  # Minimum width
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        # Generate markdown table
        for i, row in enumerate(rows):
            result += '|'
            for j, cell in enumerate(row):
                result += f" {self.format_cell(cell, col_widths[j])} |"
            result += '\n'
            
            # Add separator after header
            if i == 0:
                result += '|'
                for width in col_widths:
                    result += f" {'-' * width} |"
                result += '\n'

        return result + '\n'

class CodeBlockFormatter:
    def format_block(self, code_html: str) -> str:
        """Convert HTML code block to markdown"""
        soup = BeautifulSoup(code_html, 'html.parser')
        code = soup.get_text()
        code = html.unescape(code)
        code = code.strip()
        return f"```\n{code}\n```\n"

def format_tables(content: str) -> str:
    """Format all tables in content"""
    formatter = TableFormatter()
    soup = BeautifulSoup(content, 'html.parser')
    
    for table in soup.find_all('table'):
        markdown_table = formatter.convert_table(str(table))
        table.replace_with(BeautifulSoup(markdown_table, 'html.parser'))
    
    return str(soup)

def format_code_blocks(content: str) -> str:
    """Format all code blocks in content"""
    formatter = CodeBlockFormatter()
    soup = BeautifulSoup(content, 'html.parser')
    
    for pre in soup.find_all('pre'):
        markdown_code = formatter.format_block(str(pre))
        pre.replace_with(BeautifulSoup(markdown_code, 'html.parser'))
    
    return str(soup) 