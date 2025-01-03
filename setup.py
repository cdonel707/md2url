from setuptools import setup, find_packages

setup(
    name="urltomarkdown",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'fastapi==0.110.0',
        'uvicorn==0.27.1',
        'markdown2==2.4.12',
        'readability-lxml==0.8.1',
        'beautifulsoup4==4.12.3',
        'requests==2.31.0',
        'html2text==2020.1.16',
        'slowapi==0.1.9',
        'validators==0.22.0',
        'python-multipart==0.0.9',
        'aiohttp==3.9.3',
        'lxml[html_clean]>=5.1.0'
    ],
    entry_points={
        'console_scripts': [
            'url2md=app.cli:main',
        ],
    },
) 