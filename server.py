"""
Production MCP Web Scraper Server - Main Entry Point
Built with official MCP Python SDK using Streamable HTTP transport
"""
import logging
import os
from mcp.server.fastmcp import FastMCP

# Import tools
from tools.search import register_search_tools
from tools.scraping import register_scraping_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server with Streamable HTTP
mcp = FastMCP(
    name="web-scraper",
    description="Advanced web scraping and search MCP server with DuckDuckGo, article extraction, and intelligent scraping",
    stateless_http=True,
    json_response=True
)

# Register all tools
logger.info("Registering search tools...")
register_search_tools(mcp)

logger.info("Registering scraping tools...")
register_scraping_tools(mcp)

logger.info("All tools registered successfully")


if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
    
    # Run with Streamable HTTP transport
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port
    )