from bs4 import BeautifulSoup

def format_tables(content: str) -> str:
    """Format all tables in content"""
    soup = BeautifulSoup(content, 'html.parser')
    
    for table in soup.find_all('table'):
        markdown_table = convert_table(str(table))
        table.replace_with(BeautifulSoup(markdown_table, 'html.parser'))
    
    return str(soup)

def convert_table(table_html: str) -> str:
    """Convert HTML table to markdown format"""
    soup = BeautifulSoup(table_html, 'html.parser')
    rows = []
    
    # Extract headers
    headers = []
    for th in soup.find_all('th'):
        headers.append(th.get_text().strip())
    
    if headers:
        rows.append('| ' + ' | '.join(headers) + ' |')
        rows.append('| ' + ' | '.join(['---' for _ in headers]) + ' |')
    
    # Extract data rows
    for tr in soup.find_all('tr'):
        cells = []
        for td in tr.find_all(['td', 'th']):
            cells.append(td.get_text().strip())
        if cells and not (len(cells) == len(headers) and all(cell in headers for cell in cells)):
            rows.append('| ' + ' | '.join(cells) + ' |')
    
    return '\n'.join(rows) 