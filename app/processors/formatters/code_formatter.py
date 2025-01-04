from bs4 import BeautifulSoup
import re

def format_code_blocks(content: str) -> str:
    """Format all code blocks in content"""
    soup = BeautifulSoup(content, 'html.parser')
    
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            language = detect_language(code.get('class', []))
            formatted = f"```{language}\n{code.get_text().strip()}\n```"
            pre.replace_with(BeautifulSoup(formatted, 'html.parser'))
    
    return str(soup)

def detect_language(classes: list) -> str:
    """Detect language from code block classes"""
    for class_name in classes:
        if class_name.startswith(('language-', 'lang-')):
            return class_name.split('-')[1]
    return '' 