import pytest
from app import get_reader_for_url
from app.processors.readers.html_reader import HTMLReader
from app.processors.readers.apple_reader import AppleReader
from app.processors.readers.stack_reader import StackOverflowReader

def test_reader_factory():
    assert isinstance(get_reader_for_url("https://example.com"), HTMLReader)
    assert isinstance(get_reader_for_url("https://developer.apple.com/doc"), AppleReader)
    assert isinstance(get_reader_for_url("https://stackoverflow.com/q/1"), StackOverflowReader)

@pytest.mark.asyncio
async def test_html_reader():
    reader = HTMLReader()
    markdown, title = await reader.read_url(
        "https://example.com",
        inline_title=True,
        ignore_links=False
    )
    assert markdown
    assert title

@pytest.mark.asyncio
async def test_stack_reader():
    reader = StackOverflowReader()
    markdown, title = await reader.read_url(
        "https://stackoverflow.com/questions/1/test-question",
        inline_title=True,
        ignore_links=False
    )
    assert markdown
    assert "## Answer" in markdown 