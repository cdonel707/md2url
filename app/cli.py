import asyncio
import argparse
import sys
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import aiohttp
import validators
from app.processors.readers import get_reader_for_url

async def get_page_links(url: str, base_domain: str) -> set:
    """Get all links from a page that match the base domain"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                links = set()
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)
                    
                    # Only include links from same domain
                    if parsed.netloc == base_domain and '#' not in href:
                        links.add(full_url)
                        
                return links
    except Exception as e:
        print(f"Error getting links from {url}: {str(e)}", file=sys.stderr)
        return set()

async def convert_url(url: str, title: bool = False, links: bool = True, output: str = None,
                     recursive: bool = False, max_depth: float = 1) -> None:
    """Convert URL to markdown and save or print to stdout"""
    # Keep track of processed URLs to avoid loops
    if not hasattr(convert_url, 'processed_urls'):
        convert_url.processed_urls = set()

    # Skip if already processed
    if url in convert_url.processed_urls:
        return
    convert_url.processed_urls.add(url)

    try:
        # Process the initial URL
        reader = get_reader_for_url(url)
        markdown, page_title = await reader.read_url(url, title, not links)
        
        if output:
            # Get domain for folder structure
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Create domain folder if it doesn't exist
            import os
            domain_folder = os.path.join('markdown', domain)
            os.makedirs(domain_folder, exist_ok=True)
            
            # Generate filename from URL if not specified
            if output == 'auto':
                filename = parsed_url.path.strip('/').replace('/', '-') or 'index'
                output = os.path.join(domain_folder, f"{filename}.mdx")
            else:
                output = os.path.join(domain_folder, output)
            
            # Write to file
            with open(output, 'w', encoding='utf-8') as f:
                if title and page_title:
                    f.write(f"---\ntitle: {page_title}\nsource: {url}\n---\n\n")
                f.write(markdown)
            print(f"Successfully wrote markdown to {output}")
        else:
            print(markdown)
            
        # Handle recursive processing
        if recursive and (max_depth == float('inf') or max_depth > 0):
            base_domain = urlparse(url).netloc
            links = await get_page_links(url, base_domain)
            
            for link in links:
                if link not in convert_url.processed_urls:  # Only process new URLs
                    parsed = urlparse(link)
                    filename = parsed.path.strip('/').replace('/', '-') or 'index'
                    output_file = f"{filename}.mdx"
                    
                    print(f"\nProcessing: {link}")
                    await asyncio.sleep(1)  # Be nice to the server
                    await convert_url(
                        url=link,
                        title=title,
                        links=links,
                        output=output_file if output else None,
                        recursive=True,
                        max_depth=max_depth - 1 if max_depth != float('inf') else float('inf')
                    )
                
    except Exception as e:
        print(f"Error processing {url}: {str(e)}", file=sys.stderr)
        if not recursive:  # Only exit if this is the main URL
            sys.exit(1)

def get_yes_no_input(prompt: str) -> bool:
    """Get yes/no input from user"""
    while True:
        response = input(f"{prompt} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def get_url_input() -> str:
    """Get and validate URL input from user"""
    while True:
        url = input("Enter the URL to convert: ").strip()
        if validators.url(url):
            return url
        print("Please enter a valid URL (e.g., https://example.com)")

def get_output_input() -> str:
    """Get output file preference from user"""
    while True:
        print("\nOutput options:")
        print("1. Print to screen")
        print("2. Save to specific file")
        print("3. Auto-generate filename from URL")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            return None
        elif choice == "2":
            return input("Enter the output filename: ").strip()
        elif choice == "3":
            return "auto"
        print("Please enter 1, 2, or 3")

def get_depth_input() -> int:
    """Get recursion depth from user"""
    while True:
        try:
            print("\nRecursion depth options:")
            print("1. Limited depth (1-5 levels)")
            print("2. Unlimited depth (crawl entire site)")
            
            choice = input("Choose an option (1-2): ").strip()
            
            if choice == "1":
                depth = int(input("Enter maximum recursion depth (1-5): ").strip())
                if 1 <= depth <= 5:
                    return depth
                print("Please enter a number between 1 and 5")
            elif choice == "2":
                print("\nWarning: This will attempt to convert every page on the site.")
                print("This could take a long time and generate many files.")
                if get_yes_no_input("Are you sure you want to continue?"):
                    return float('inf')  # Unlimited depth
                
            else:
                print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number")

def main():
    print("Welcome to URL to Markdown Converter!")
    print("=====================================")
    
    # Get URL
    url = get_url_input()
    
    # Get title preference
    title = get_yes_no_input("Include page title as heading?")
    
    # Get links preference
    links = get_yes_no_input("Preserve links in the output?")
    
    # Get output preference
    output = get_output_input()
    
    # Get recursive preference
    recursive = get_yes_no_input("Process links recursively?")
    
    # Get depth if recursive
    max_depth = get_depth_input() if recursive else 1
    
    print("\nStarting conversion...")
    asyncio.run(convert_url(
        url=url,
        title=title,
        links=links,
        output=output,
        recursive=recursive,
        max_depth=max_depth
    ))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1) 