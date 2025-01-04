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
    request: Request,
    url: str = None,
    title: bool = False,
    links: bool = True,
    recursive: bool = False,
    depth: str = "1",
    output: str = "preview",
    use_fern: bool = False
):
    if not url:
        raise HTTPException(status_code=400, detail="Please provide a URL parameter")

    try:
        # Process single URL first
        reader = get_reader_for_url(url)
        content, page_title = await reader.read_url(url, title, not links)

        # Apply Fern styling if requested
        if use_fern:
            content = await convert_to_fern_style(content)

        # Handle recursive processing if requested
        if recursive and depth != "1":
            temp_dir = tempfile.mkdtemp()
            try:
                # Save first page
                save_to_file(temp_dir, "index.mdx", content, page_title, url)
                
                # Process additional pages up to depth
                max_depth = float('inf') if depth == "Unlimited" else int(depth)
                await process_recursive_urls(url, temp_dir, max_depth, title, links, use_fern)

                # Create zip file with all pages
                return create_zip_response(temp_dir)
            finally:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
        
        # Return single page content
        return PlainTextResponse(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

async def process_recursive_urls(base_url: str, temp_dir: str, max_depth: int, title: bool, links: bool, use_fern: bool):
    processed_urls = {base_url}
    current_depth = 1
    
    while current_depth < max_depth:
        new_urls = set()
        for url in processed_urls:
            try:
                sub_urls = await get_page_links(url)
                for sub_url in sub_urls:
                    if sub_url not in processed_urls:
                        reader = get_reader_for_url(sub_url)
                        content, page_title = await reader.read_url(sub_url, title, not links)
                        
                        if use_fern:
                            content = await convert_to_fern_style(content)
                            
                        filename = generate_filename(sub_url)
                        save_to_file(temp_dir, filename, content, page_title, sub_url)
                        new_urls.add(sub_url)
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
                continue
                
        if not new_urls:
            break
            
        processed_urls.update(new_urls)
        current_depth += 1

def generate_filename(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")
    filename = "index.mdx" if not path else f"{path.replace('/', '-')}.mdx"
    return filename[:95] + ".mdx" if len(filename) > 100 else filename

def save_to_file(temp_dir: str, filename: str, content: str, title: str, url: str):
    with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
        f.write(f"---\ntitle: {title or 'Untitled'}\n")
        f.write(f"source: {url}\n")
        f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n")
        f.write(content)

def create_zip_response(temp_dir: str) -> Response:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zip_path = os.path.join('markdown-export', file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    zipf.writestr(zip_path, f.read())
    
    shutil.rmtree(temp_dir)
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename=markdown-export.zip'}
    )

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")