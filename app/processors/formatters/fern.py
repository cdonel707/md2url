from bs4 import BeautifulSoup
import re

async def convert_to_fern_style(content: str) -> str:
    """
    Convert markdown content to Fern-style formatting.
    Fern style includes:
    - Clean headers with proper spacing
    - Code block language tags
    - Properly formatted lists
    - Table alignments
    - Blockquote styling
    """
    # Add spacing around headers
    content = re.sub(r'(#{1,6}.*?)\n', r'\1\n\n', content)
    
    # Clean up code blocks
    content = re.sub(r'```(\w+)?\n', r'```\1\n', content)
    content = re.sub(r'\n```\n', r'\n```\n\n', content)
    
    # Format lists with proper spacing
    content = re.sub(r'(\n- .*?)(\n[^-\n])', r'\1\n\2', content)
    
    # Clean up tables
    content = re.sub(r'\n\|.*?\|\n', lambda m: f"\n{m.group().strip()}\n\n", content)
    
    # Format blockquotes
    content = re.sub(r'(^|\n)> (.*?)(\n[^>]|\n$|$)', r'\1> \2\n\n\3', content, flags=re.MULTILINE)
    
    # Add proper spacing around sections
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Add frontmatter markers if not present
    if not content.startswith('---\n'):
        content = f"---\ntype: documentation\nstatus: published\n---\n\n{content}"
    
    return content

def format_code_blocks(content: str) -> str:
    """
    Enhance code blocks with language tags and proper formatting
    """
    code_pattern = re.compile(r'```(.*?)\n(.*?)```', re.DOTALL)
    
    def replace_code_block(match):
        lang = match.group(1).strip() or 'text'
        code = match.group(2).rstrip()
        return f"```{lang}\n{code}\n```\n"
    
    return code_pattern.sub(replace_code_block, content)

def format_tables(content: str) -> str:
    """
    Format tables with proper alignment and spacing
    """
    lines = content.split('\n')
    formatted_lines = []
    in_table = False
    
    for line in lines:
        if line.startswith('|'):
            if not in_table:
                formatted_lines.append('')  # Add space before table
                in_table = True
            formatted_lines.append(line)
        else:
            if in_table:
                formatted_lines.append('')  # Add space after table
                in_table = False
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines) 