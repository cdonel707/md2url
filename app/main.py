from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import validators
from fastapi.templating import Jinja2Templates
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse, urljoin
from starlette.config import Config
from app.processors.readers import get_reader_for_url
import io
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
import re
import aiohttp
from sse_starlette.sse import EventSourceResponse
import asyncio
from functools import lru_cache
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.processors.formatters.fern import convert_to_fern_style
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

# Load environment variables
load_dotenv()

# Get environment variables with defaults
WORKERS = int(os.getenv('WORKERS', '4'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
RELOAD = os.getenv('RELOAD', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', '8000'))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="URL to Markdown Converter",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Error handling middleware
class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                content=str(e),
                status_code=500
            )

# Add middleware
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates path
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# Serve the index page at root
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("Root endpoint called - serving index.html")
    try:
        response = templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
        logger.info("Template rendered successfully")
        return response
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Add a separate health check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Directory contents: {os.listdir('.')}")
    logger.info(f"App directory contents: {os.listdir('./app')}")

@app.get("/convert")
async def convert_url(
    url: str,
    title: bool = False,
    links: bool = True,
    recursive: bool = False,
    use_fern: bool = False,
    output: str = "preview"
):
    logger.info(f"Converting URL: {url} (recursive: {recursive})")
    
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    try:
        if recursive:
            # Create temporary directory for files
            with tempfile.TemporaryDirectory() as temp_dir:
                processed_urls = set()
                await process_url_recursive(
                    url=url,
                    temp_dir=temp_dir,
                    processed_urls=processed_urls,
                    title=title,
                    links=links,
                    use_fern=use_fern
                )
                
                # Create ZIP file from processed files
                return create_zip_response(temp_dir)
        else:
            # Single file processing
            reader = get_reader_for_url(url)
            content, page_title = await reader.read_url(url, title, not links)
            
            if use_fern:
                content = await convert_to_fern_style(content)
            
            return PlainTextResponse(content)
            
    except Exception as e:
        logger.error(f"Error converting URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_url_recursive(url: str, temp_dir: str, processed_urls: set, 
                              title: bool, links: bool, use_fern: bool, depth: int = 0):
    """Process a URL and its linked pages recursively"""
    if depth > 5 or url in processed_urls:  # Limit recursion depth
        return
    
    processed_urls.add(url)
    logger.info(f"Processing URL (depth {depth}): {url}")
    
    try:
        # Process current page
        reader = get_reader_for_url(url)
        content, page_title = await reader.read_url(url, title, not links)
        
        if use_fern:
            content = await convert_to_fern_style(content)
        
        # Generate filename from URL path
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        
        if not path:
            filename = "index.md"
        else:
            # Replace slashes with hyphens and remove file extensions
            filename = path.replace('/', '-').rstrip('.html').rstrip('.htm')
            # Add .md extension if not present
            if not filename.endswith('.md'):
                filename += '.md'
        
        # Save content
        filepath = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\ntitle: {page_title or 'Untitled'}\n")
            f.write(f"source: {url}\n")
            f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n")
            f.write(content)
        
        # Process linked pages
        if depth < 5:
            linked_urls = await get_page_links(url)
            for linked_url in linked_urls:
                if linked_url not in processed_urls:
                    await process_url_recursive(
                        url=linked_url,
                        temp_dir=temp_dir,
                        processed_urls=processed_urls,
                        title=title,
                        links=links,
                        use_fern=use_fern,
                        depth=depth + 1
                    )
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")

def create_zip_response(temp_dir: str) -> Response:
    """Create a ZIP file from the temporary directory"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arc_path)
    
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename=markdown-export.zip'}
    )

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")