import pytest
from app.processors.html_processor import process_html
from app.processors.formatters import format_tables, format_code_blocks
from app.processors.filters import apply_filters

def test_process_html_basic():
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test.</p>
        </body>
    </html>
    """
    markdown, title = process_html(html, inline_title=True)
    assert "# Test Page" in markdown
    assert "Hello World" in markdown
    assert "This is a test" in markdown
    assert title == "Test Page"

def test_process_html_with_code():
    html = """
    <pre><code>def hello():
    print("Hello World")</code></pre>
    """
    markdown, _ = process_html(html)
    assert "```" in markdown
    assert "def hello():" in markdown
    assert 'print("Hello World")' in markdown

def test_process_html_with_table():
    html = """
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Cell 1</td><td>Cell 2</td></tr>
    </table>
    """
    markdown, _ = process_html(html)
    assert "| Header 1 | Header 2 |" in markdown
    assert "| Cell 1  | Cell 2  |" in markdown

def test_filters():
    content = "[test](/relative/path)"
    filtered = apply_filters("https://example.com", content)
    assert "https://example.com/relative/path" in filtered 