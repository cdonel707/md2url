from setuptools import setup, find_packages

# Hardcode the long description since file reading is causing issues
long_description = """
# URL to Markdown Converter

A FastAPI application that converts web pages to clean, readable markdown format.

## Installation

```bash
pip install urltomarkdown
```

## Usage

### Command Line
```bash
url2md
```

Or use the interactive mode:
```bash
url2md --interactive
```

### API
```python
from urltomarkdown import convert_url

markdown = await convert_url("https://example.com")
print(markdown)
```

## Features

- Convert any web page to markdown
- Clean and readable output
- Support for code blocks with syntax highlighting
- Table formatting
- Link handling options
- Rate limiting
- Caching
- API documentation
"""

setup(
    name="urltomarkdown",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert web pages to clean markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/urltomarkdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.110.0",
        "uvicorn==0.27.1",
        "python-multipart==0.0.9",
        "jinja2==3.1.2",
        "aiohttp==3.9.3",
        "beautifulsoup4==4.12.3",
        "html2text==2020.1.16",
        "readability-lxml==0.8.1",
        "validators==0.22.0",
        "pyyaml==6.0.1",
        "slowapi==0.1.9",
        "starlette==0.36.3",
        "lxml==5.1.0",
        "soupsieve==2.5",
        "typing-extensions>=4.12.2",
        "sse-starlette==1.6.5",
        "websockets==12.0",
        "httpx>=0.25.2",
        "asgiref>=3.7.2",
        "gunicorn==21.2.0",
        "uvicorn[standard]==0.27.1",
        "python-dotenv==1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'url2md=app.cli:main',
        ],
    },
) 