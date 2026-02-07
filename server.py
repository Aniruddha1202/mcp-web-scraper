import os
import base64
import asyncio
from typing import Any, Sequence
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import mcp.types as types
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from duckduckgo_search import DDGS
from qdrant_client import QdrantClient

# --- INITIALIZATION ---
app = FastAPI()
mcp_server = Server("ultimate-research-mcp")

# --- QDRANT MEMORY SETUP ---
# Running in-memory (:memory:) for speed and no-config. 
# Note: Data wipes if the Render server restarts.
q_client = QdrantClient(":memory:") 
COLLECTION = "research_notes"

if not q_client.collection_exists(COLLECTION):
    q_client.create_collection(
        collection_name=COLLECTION,
        vectors_config=q_client.get_fastembed_vector_params()
    )

# --- TOOLS DEFINITION ---
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_web", 
            description="Search the internet for real-time information.", 
            inputSchema={"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}
        ),
        Tool(
            name="scrape_url", 
            description="Visit a URL and extract all text as Markdown.", 
            inputSchema={"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}
        ),
        Tool(
            name="store_memory", 
            description="Save a snippet of info or code to long-term vector memory.", 
            inputSchema={"type":"object","properties":{"text":{"type":"string"},"metadata":{"type":"string"}},"required":["text"]}
        ),
        Tool(
            name="retrieve_memory", 
            description="Search your own saved memories for relevant information.", 
            inputSchema={"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}
        ),
    ]

# --- TOOL LOGIC ---
@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    try:
        if name == "search_web":
            query = arguments["query"]
            results = DDGS().text(query, max_results=5)
            formatted = "\n".join([f"- {r['title']}: {r['href']}" for r in results])
            return [TextContent(type="text", text=f"Search Results for '{query}':\n{formatted}")]
            
        elif name == "scrape_url":
            url = arguments["url"]
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=60000)
                # Auto-scroll to load lazy content
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
                content = md(await page.content())
                await browser.close()
                return [TextContent(type="text", text=content[:15000])] # Limit to 15k chars for LLM safety
                
        elif name == "store_memory":
            text = arguments["text"]
            ref = arguments.get("metadata", "general")
            q_client.add(collection_name=COLLECTION, documents=[text], metadata=[{"ref": ref}])
            return [TextContent(type="text", text=f"✅ Memory stored successfully.")]

        elif name == "retrieve_memory":
            query = arguments["query"]
            hits = q_client.query(collection_name=COLLECTION, query_text=query, limit=3)
            if not hits:
                return [TextContent(type="text", text="No matching memories found.")]
            formatted = "\n---\n".join([f"[Ref: {h.metadata.get('ref')}] {h.document}" for h in hits])
            return [TextContent(type="text", text=f"Relevant Memories:\n{formatted}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}", isError=True)]

# --- SSE TRANSPORT (NO AUTH) ---
sse = SseServerTransport("/messages")

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(
            streams[0], 
            streams[1], 
            mcp_server.create_initialization_options()
        )

@app.post("/messages")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    # PORT is set by Render
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)