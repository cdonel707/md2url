# URL to Markdown Converter

A Python web service that converts web pages to markdown format. Inspired by [Heck Yeah Markdown](http://heckyesmarkdown.com).

## Features

- Converts web pages to clean, readable markdown
- Special handling for StackOverflow and Apple Developer documentation
- Support for tables and code blocks
- Rate limiting protection
- CORS support
- Optional inline titles
- Optional link preservation

## API Usage

### GET Request

Convert a URL to markdown:

```
GET /?url=https://example.com&title=true&links=true
```

Parameters:
- `url`: The webpage URL to convert (required)
- `title`: Whether to include the page title (optional, default: false)
- `links`: Whether to preserve links (optional, default: true)

### POST Request

Convert HTML content to markdown:

```
POST /?title=true&links=true
Content-Type: application/x-www-form-urlencoded

html=<html>...</html>&url=https://example.com
```

Parameters:
- `html`: The HTML content to convert (required)
- `url`: Original URL for reference (optional)
- `title`: Whether to include the page title (optional, default: false)
- `links`: Whether to preserve links (optional, default: true)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Development

Run tests:
```bash
pytest
```

## License

MIT License - See LICENSE file for details