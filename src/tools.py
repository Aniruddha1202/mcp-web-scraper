"""Web scraping and search tools for MCP server"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import re
from urllib.parse import urljoin, urlparse
from duckduckgo_search import DDGS
import trafilatura
from newspaper import Article
import time


class WebScraper:
    """Web scraping functionality"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def scrape_html(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape HTML content from a URL
        
        Args:
            url: The URL to scrape
            selector: Optional CSS selector to filter content
            
        Returns:
            Dict containing scraped content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            if selector:
                elements = soup.select(selector)
                content = [self._clean_text(el.get_text()) for el in elements]
                html = [str(el) for el in elements]
            else:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                content = [self._clean_text(soup.get_text())]
                html = [str(soup)]
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "html": html,
                "count": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def extract_links(self, url: str, filter_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract all links from a webpage
        
        Args:
            url: The URL to scrape
            filter_pattern: Optional regex pattern to filter links
            
        Returns:
            Dict containing extracted links
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(url, href)
                
                # Filter by pattern if provided
                if filter_pattern:
                    if not re.search(filter_pattern, absolute_url):
                        continue
                
                links.append({
                    "text": self._clean_text(a_tag.get_text()),
                    "url": absolute_url
                })
            
            return {
                "success": True,
                "source_url": url,
                "links": links,
                "count": len(links)
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def extract_metadata(self, url: str) -> Dict[str, Any]:
        """
        Extract metadata from a webpage (title, description, etc.)
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict containing page metadata
        """
        try:
            response = self.session.get(url, timeout=10)
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
            
            # Title
            if soup.title:
                metadata["title"] = self._clean_text(soup.title.string)
            
            # Meta tags
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
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def scrape_table(self, url: str, table_index: int = 0) -> Dict[str, Any]:
        """
        Extract table data from a webpage
        
        Args:
            url: The URL to scrape
            table_index: Index of the table to extract (0-based)
            
        Returns:
            Dict containing table data
        """
        try:
            response = self.session.get(url, timeout=10)
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
                headers = [self._clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            # Extract rows
            for tr in table.find_all('tr'):
                cells = [self._clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                if cells and cells != headers:
                    rows.append(cells)
            
            return {
                "success": True,
                "url": url,
                "headers": headers,
                "rows": rows,
                "row_count": len(rows)
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def web_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            Dict containing search results
        """
        try:
            results = []
            
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "DuckDuckGo"
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def search_and_scrape(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web and scrape content from top results
        
        Args:
            query: Search query
            num_results: Number of results to scrape (default: 5)
            
        Returns:
            Dict containing search results with scraped content
        """
        try:
            # First, search
            search_result = await self.web_search(query, max_results=num_results)
            
            if not search_result.get("success"):
                return search_result
            
            # Then scrape each result
            enriched_results = []
            
            for result in search_result["results"][:num_results]:
                url = result["url"]
                
                # Extract main content using trafilatura
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        content = trafilatura.extract(
                            downloaded,
                            include_comments=False,
                            include_tables=True,
                            no_fallback=False
                        )
                        
                        enriched_results.append({
                            "title": result["title"],
                            "url": url,
                            "snippet": result["snippet"],
                            "content": content if content else "Content extraction failed",
                            "content_length": len(content) if content else 0
                        })
                    else:
                        enriched_results.append({
                            **result,
                            "content": "Failed to download page",
                            "content_length": 0
                        })
                        
                except Exception as scrape_error:
                    enriched_results.append({
                        **result,
                        "content": f"Scraping error: {str(scrape_error)}",
                        "content_length": 0
                    })
                
                # Small delay to be polite
                time.sleep(0.5)
            
            return {
                "success": True,
                "query": query,
                "results": enriched_results,
                "count": len(enriched_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def extract_article(self, url: str) -> Dict[str, Any]:
        """
        Extract clean article content using newspaper3k and trafilatura
        
        Args:
            url: Article URL
            
        Returns:
            Dict containing article content and metadata
        """
        try:
            # Method 1: newspaper3k
            article = Article(url)
            article.download()
            article.parse()
            
            # Method 2: trafilatura (fallback/enhancement)
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
                "summary": article.summary if hasattr(article, 'summary') else None,
                "keywords": article.keywords if hasattr(article, 'keywords') else [],
                "content_length": len(content) if content else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def smart_search(self, query: str, mode: str = "comprehensive") -> Dict[str, Any]:
        """
        Intelligent search with different modes
        
        Args:
            query: Search query
            mode: Search mode - "quick" (3 results), "standard" (5 results), 
                  "comprehensive" (10 results with full scraping)
            
        Returns:
            Dict containing intelligent search results
        """
        try:
            if mode == "quick":
                num_results = 3
                scrape_content = False
            elif mode == "standard":
                num_results = 5
                scrape_content = False
            else:  # comprehensive
                num_results = 10
                scrape_content = True
            
            if scrape_content:
                return await self.search_and_scrape(query, num_results)
            else:
                return await self.web_search(query, num_results)
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def news_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for news articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Dict containing news search results
        """
        try:
            results = []
            
            with DDGS() as ddgs:
                news_results = ddgs.news(query, max_results=max_results)
                
                for result in news_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("body", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", ""),
                        "image": result.get("image", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()