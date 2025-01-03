from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import validators

from app.processors.readers import get_reader_for_url
from app.processors.html_processor import process_html

app = FastAPI(title="URL to Markdown Converter")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limit error handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", response_class=PlainTextResponse)
@limiter.limit("5/30seconds")
async def convert_url(
    request: Request,
    url: str,
    title: bool = False,
    links: bool = True
):
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Please specify a valid url parameter")
    
    reader = get_reader_for_url(url)
    markdown, page_title = await reader.read_url(url, title, not links)
    
    response = PlainTextResponse(markdown)
    if page_title:
        response.headers["X-Title"] = page_title
    return response

@app.post("/", response_class=PlainTextResponse)
@limiter.limit("5/30seconds")
async def convert_html(
    request: Request,
    html: str,
    url: str = None,
    title: bool = False,
    links: bool = True
):
    try:
        markdown, page_title = process_html(html, url, title, not links)
        response = PlainTextResponse(markdown)
        if page_title:
            response.headers["X-Title"] = page_title
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not parse that document") 