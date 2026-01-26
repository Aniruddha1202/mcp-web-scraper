"""
Search Tools Module
Contains all web search related tools: web_search, news_search, search_and_scrape, smart_search
"""
import logging
from typing import Any
from duckduckgo_search import DDGS
import trafilatura
import time

logger = logging.getLogger(__name__)


def register_search_tools(mcp):
    """Register all search tools with the MCP server"""
    
    @mcp.tool()
    def web_search(query: str, max_results: int = 10) -> dict[str, Any]:
        """
        Search the web using DuckDuckGo and return top results.
        
        Args:
            query: Search query (e.g., 'latest AI news', 'python tutorials', 'restaurants in Paris')
            max_results: Maximum number of results to return (default: 10, max: 20)
        
        Returns:
            Dictionary containing search results with titles, URLs, and snippets
        
        Example:
            web_search("machine learning tutorials", max_results=5)
        """
        try:
            logger.info(f"Web search: {query}")
            results = []
            
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=min(max_results, 20))
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", "")
                    })
            
            logger.info(f"Found {len(results)} results")
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"success": False, "query": query, "error": str(e)}
    
    
    @mcp.tool()
    def news_search(query: str, max_results: int = 10) -> dict[str, Any]:
        """
        Search for news articles with dates, sources, and images.
        
        Args:
            query: News search query (e.g., 'climate change', 'technology news', 'sports updates')
            max_results: Maximum number of news articles (default: 10, max: 20)
        
        Returns:
            Dictionary containing news articles with metadata including date and source
        
        Example:
            news_search("artificial intelligence", max_results=5)
        """
        try:
            logger.info(f"News search: {query}")
            results = []
            
            with DDGS() as ddgs:
                news_results = ddgs.news(query, max_results=min(max_results, 20))
                for result in news_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("body", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", ""),
                        "image": result.get("image", "")
                    })
            
            logger.info(f"Found {len(results)} news articles")
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"News search error: {e}")
            return {"success": False, "query": query, "error": str(e)}
    
    
    @mcp.tool()
    def search_and_scrape(query: str, num_results: int = 5) -> dict[str, Any]:
        """
        Search the web and automatically scrape full content from top results.
        Perfect for research - provides complete article content, not just snippets.
        
        Args:
            query: Search query for research
            num_results: Number of results to scrape (default: 5, max: 10)
        
        Returns:
            Dictionary with search results including full scraped content from each page
        
        Example:
            search_and_scrape("quantum computing explained", num_results=3)
        """
        try:
            logger.info(f"Search and scrape: {query}")
            num_results = min(num_results, 10)
            
            # First, search
            search_result = web_search(query, num_results)
            if not search_result.get("success"):
                return search_result
            
            # Then scrape each result
            enriched_results = []
            for idx, result in enumerate(search_result["results"][:num_results], 1):
                url = result["url"]
                logger.info(f"Scraping {idx}/{num_results}: {url}")
                
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
                except Exception as e:
                    logger.error(f"Scraping error for {url}: {e}")
                    enriched_results.append({
                        **result,
                        "content": f"Error: {str(e)}",
                        "content_length": 0
                    })
                
                # Be polite to servers
                if idx < num_results:
                    time.sleep(0.5)
            
            return {
                "success": True,
                "query": query,
                "results": enriched_results,
                "count": len(enriched_results)
            }
        except Exception as e:
            logger.error(f"Search and scrape error: {e}")
            return {"success": False, "query": query, "error": str(e)}
    
    
    @mcp.tool()
    def smart_search(query: str, mode: str = "comprehensive") -> dict[str, Any]:
        """
        Intelligent search with different modes for speed vs detail tradeoff.
        
        Args:
            query: Search query
            mode: Search mode - 'quick' (3 results), 'standard' (5 results), or 'comprehensive' (10 results with full scraping)
        
        Returns:
            Dictionary with search results optimized for the selected mode
        
        Example:
            smart_search("climate change solutions", mode="comprehensive")
        """
        try:
            logger.info(f"Smart search ({mode}): {query}")
            
            if mode == "quick":
                return web_search(query, 3)
            elif mode == "standard":
                return web_search(query, 5)
            else:  # comprehensive
                return search_and_scrape(query, 10)
        except Exception as e:
            logger.error(f"Smart search error: {e}")
            return {"success": False, "query": query, "error": str(e)}