"""
MCP Web Scraper Tools Package
Contains all search and scraping tools for the MCP server
"""

from .search import register_search_tools
from .scraping import register_scraping_tools

__all__ = [
    'register_search_tools',
    'register_scraping_tools'
]