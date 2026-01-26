"""
Scraping Tools Module
Contains all web scraping related tools: scrape_html, extract_article, extract_links, extract_metadata, scrape_table
"""
import logging
from typing import Any
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import trafilatura
from urllib.parse import urljoin
import re
from utils.helpers import clean_text

logger = logging.getLogger(__name__)

# Initialize HTTP session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})


def register_scraping_tools(mcp):
    """Register all scraping tools with the MCP server"""
    
    @mcp.tool()
    def scrape_html(url: str, selector: str = None) -> dict[str, Any]:
        """
        Scrape HTML content from a URL with optional CSS selector filtering.
        
        Args:
            url: The URL to scrape
            selector: Optional CSS selector to filter specific elements (e.g., 'h1', '.article-content', '#main')
        
        Returns:
            Dictionary containing scraped content
        
        Example:
            scrape_html("https://example.com", selector="h1, .content")
        """
        try:
            logger.info(f"Scraping HTML from: {url}")
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            if selector:
                elements = soup.select(selector)
                content = [clean_text(el.get_text()) for el in elements]
            else:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                content = [clean_text(soup.get_text())]
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "count": len(content)
            }
        except Exception as e:
            logger.error(f"Scrape HTML error for {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}
    
    
    @mcp.tool()
    def extract_article(url: str) -> dict[str, Any]:
        """
        Extract clean article content from news sites and blogs.
        Automatically removes ads, navigation, sidebars, and other clutter.
        
        Args:
            url: Article URL to extract content from
        
        Returns:
            Dictionary with article content, title, authors, publish date, and metadata
        
        Example:
            extract_article("https://example.com/article/ai-breakthrough")
        """
        try:
            logger.info(f"Extracting article from: {url}")
            
            # Try newspaper3k first
            article = Article(url)
            article.download()
            article.parse()
            
            # Fallback to trafilatura for better content extraction
            downloaded = trafilatura.fetch_url(url)
            trafilatura_content = None
            if downloaded:
                trafilatura_content = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=True
                )
            
            # Use the better extraction
            content = article.text if article.text else trafilatura_content
            
            return {
                "success": True,
                "url": url,
                "title": article.title,
                "authors": article.authors,
                "publish_date": str(article.publish_date) if article.publish_date else None,
                "top_image": article.top_image,
                "content": content,
                "content_length": len(content) if content else 0
            }
        except Exception as e:
            logger.error(f"Article extraction error for {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}
    
    
    @mcp.tool()
    def extract_links(url: str, filter_pattern: str = None) -> dict[str, Any]:
        """
        Extract all links from a webpage with optional regex filtering.
        
        Args:
            url: The URL to scrape links from
            filter_pattern: Optional regex pattern to filter links (e.g., '.*\\.pdf$' for PDF files)
        
        Returns:
            Dictionary containing all extracted links with their text and URLs
        
        Example:
            extract_links("https://example.com", filter_pattern=".*article.*")
        """
        try:
            logger.info(f"Extracting links from: {url}")
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(url, href)
                
                # Apply filter if provided
                if filter_pattern and not re.search(filter_pattern, absolute_url):
                    continue
                
                links.append({
                    "text": clean_text(a_tag.get_text()),
                    "url": absolute_url
                })
            
            logger.info(f"Found {len(links)} links")
            return {
                "success": True,
                "source_url": url,
                "links": links,
                "count": len(links)
            }
        except Exception as e:
            logger.error(f"Link extraction error for {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}
    
    
    @mcp.tool()
    def extract_metadata(url: str) -> dict[str, Any]:
        """
        Extract metadata from a webpage including title, description, and Open Graph tags.
        
        Args:
            url: The URL to extract metadata from
        
        Returns:
            Dictionary containing page metadata (title, description, keywords, author, Open Graph tags)
        
        Example:
            extract_metadata("https://example.com/page")
        """
        try:
            logger.info(f"Extracting metadata from: {url}")
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            metadata = {
                "title": None,
                "description": None,
                "keywords": None,
                "author": None,
                "og_title": None,
                "og_description": None,
                "og_image": None
            }
            
            # Extract title
            if soup.title:
                metadata["title"] = clean_text(soup.title.string)
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', '').lower()
                property_name = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name == 'description':
                    metadata["description"] = content
                elif name == 'keywords':
                    metadata["keywords"] = content
                elif name == 'author':
                    metadata["author"] = content
                elif property_name == 'og:title':
                    metadata["og_title"] = content
                elif property_name == 'og:description':
                    metadata["og_description"] = content
                elif property_name == 'og:image':
                    metadata["og_image"] = content
            
            return {
                "success": True,
                "url": url,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Metadata extraction error for {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}
    
    
    @mcp.tool()
    def scrape_table(url: str, table_index: int = 0) -> dict[str, Any]:
        """
        Extract table data from a webpage.
        
        Args:
            url: The URL containing the table
            table_index: Index of the table to extract (0-based, default: 0 for first table)
        
        Returns:
            Dictionary containing table headers and rows
        
        Example:
            scrape_table("https://example.com/data", table_index=1)
        """
        try:
            logger.info(f"Scraping table {table_index} from: {url}")
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            tables = soup.find_all('table')
            if not tables:
                return {
                    "success": False,
                    "url": url,
                    "error": "No tables found on page"
                }
            
            if table_index >= len(tables):
                return {
                    "success": False,
                    "url": url,
                    "error": f"Table index {table_index} out of range. Found {len(tables)} tables."
                }
            
            table = tables[table_index]
            headers = []
            rows = []
            
            # Extract headers
            header_row = table.find('thead')
            if header_row:
                headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            # Extract rows
            for tr in table.find_all('tr'):
                cells = [clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                if cells and cells != headers:
                    rows.append(cells)
            
            logger.info(f"Extracted table with {len(rows)} rows")
            return {
                "success": True,
                "url": url,
                "headers": headers,
                "rows": rows,
                "row_count": len(rows)
            }
        except Exception as e:
            logger.error(f"Table scraping error for {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}