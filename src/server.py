"""MCP Web Scraper Server - Main application"""
import logging
import asyncio
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import json
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult
)
from src.tools import WebScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="MCP Web Scraper Server",
    description="Advanced web scraping and search MCP server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Server
mcp_server = Server("web-scraper")
scraper = WebScraper()

# Define tools
TOOLS = [
    Tool(
        name="scrape_html",
        description="Scrape HTML content from a URL with optional CSS selector filtering",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                },
                "selector": {
                    "type": "string",
                    "description": "Optional CSS selector to filter content"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="extract_links",
        description="Extract all links from a webpage with optional regex filtering",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                },
                "filter_pattern": {
                    "type": "string",
                    "description": "Optional regex pattern to filter links"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="extract_metadata",
        description="Extract metadata (title, description, Open Graph tags) from a webpage",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="scrape_table",
        description="Extract table data from a webpage",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                },
                "table_index": {
                    "type": "integer",
                    "description": "Index of the table to extract (0-based, default: 0)"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="web_search",
        description="Search the web for any query and get top results with titles, URLs, and snippets",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'latest AI news', 'python tutorials', 'weather in Paris')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="search_and_scrape",
        description="Search the web and automatically scrape full content from top results - perfect for research",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to scrape (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="extract_article",
        description="Extract clean article content from news sites and blogs (removes ads, navigation, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Article URL"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="smart_search",
        description="Intelligent search with different modes: quick (3 results), standard (5 results), or comprehensive (10 results with full scraping)",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "mode": {
                    "type": "string",
                    "enum": ["quick", "standard", "comprehensive"],
                    "description": "Search mode: 'quick' for fast results, 'standard' for balanced, 'comprehensive' for deep research",
                    "default": "comprehensive"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="news_search",
        description="Search specifically for news articles with dates, sources, and images",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "News search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of news articles (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    )
]


@mcp_server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(tools=TOOLS)


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "scrape_html":
            result = await scraper.scrape_html(
                url=arguments["url"],
                selector=arguments.get("selector")
            )
        elif name == "extract_links":
            result = await scraper.extract_links(
                url=arguments["url"],
                filter_pattern=arguments.get("filter_pattern")
            )
        elif name == "extract_metadata":
            result = await scraper.extract_metadata(
                url=arguments["url"]
            )
        elif name == "scrape_table":
            result = await scraper.scrape_table(
                url=arguments["url"],
                table_index=arguments.get("table_index", 0)
            )
        elif name == "web_search":
            result = await scraper.web_search(
                query=arguments["query"],
                max_results=arguments.get("max_results", 10)
            )
        elif name == "search_and_scrape":
            result = await scraper.search_and_scrape(
                query=arguments["query"],
                num_results=arguments.get("num_results", 5)
            )
        elif name == "extract_article":
            result = await scraper.extract_article(
                url=arguments["url"]
            )
        elif name == "smart_search":
            result = await scraper.smart_search(
                query=arguments["query"],
                mode=arguments.get("mode", "comprehensive")
            )
        elif name == "news_search":
            result = await scraper.news_search(
                query=arguments["query"],
                max_results=arguments.get("max_results", 10)
            )
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2))],
            isError=True
        )


# HTTP Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MCP Web Scraper Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "mcp": "/sse (Server-Sent Events)",
            "tools": "/tools"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/tools")
async def get_tools():
    """List available tools"""
    tools_result = await list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]
    }


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication"""
    async def event_generator():
        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"status": "connected"})
            }
            
            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break
                    
                # Heartbeat
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({"timestamp": "alive"})
                }
                
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE error: {str(e)}")
    
    return EventSourceResponse(event_generator())


@app.post("/call-tool")
async def call_tool_endpoint(request: Request):
    """Direct tool call endpoint"""
    try:
        data = await request.json()
        name = data.get("name")
        arguments = data.get("arguments", {})
        
        result = await call_tool(name, arguments)
        
        return JSONResponse(content={
            "success": True,
            "result": result.content[0].text
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)