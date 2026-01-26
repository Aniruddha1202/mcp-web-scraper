# 🚀 Production MCP Web Scraper Server

A modular, production-ready MCP server built with the official MCP Python SDK. Optimized for Render deployment with clean separation of concerns.

## 📁 Project Structure

```
mcp-web-scraper/
├── server.py              # Main server entry point
├── tools/
│   ├── __init__.py       # Tools package initialization
│   ├── search.py         # Search tools (web_search, news_search, etc.)
│   └── scraping.py       # Scraping tools (scrape_html, extract_article, etc.)
├── utils/
│   ├── __init__.py       # Utils package initialization
│   └── helpers.py        # Helper functions (clean_text, validate_url)
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── config.example.json   # Claude Desktop config example
```

## ✨ Features

### 🔍 Search Tools (`tools/search.py`)
- **web_search** - DuckDuckGo web search
- **news_search** - News articles with metadata
- **search_and_scrape** - Search + content extraction
- **smart_search** - Adaptive search (quick/standard/comprehensive)

### 📄 Scraping Tools (`tools/scraping.py`)
- **scrape_html** - HTML scraping with CSS selectors
- **extract_article** - Clean article extraction
- **extract_links** - Link extraction with filtering
- **extract_metadata** - Page metadata & Open Graph
- **scrape_table** - Table data extraction

## 🚀 Quick Deploy to Render

### Step 1: Create Project Structure

```bash
mkdir mcp-web-scraper
cd mcp-web-scraper

# Create directory structure
mkdir -p tools utils

# Create all files (copy from artifacts above):
# - server.py
# - tools/__init__.py
# - tools/search.py
# - tools/scraping.py
# - utils/__init__.py
# - utils/helpers.py
# - requirements.txt
# - render.yaml
# - .gitignore
# - README.md
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Modular MCP Web Scraper"
git remote add origin https://github.com/YOUR_USERNAME/mcp-web-scraper.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render auto-detects `render.yaml`
5. Click **"Create Web Service"**
6. Wait 2-3 minutes ✨

### Step 4: Get Your URL

Your service: `https://your-app.onrender.com`
MCP endpoint: `https://your-app.onrender.com/mcp`

## 🔌 Connect to Claude Desktop

### Config Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration

```json
{
  "mcpServers": {
    "web-scraper": {
      "type": "streamable-http",
      "url": "https://your-app.onrender.com/mcp"
    }
  }
}
```

**Restart Claude Desktop** after updating config!

## 💻 Local Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/mcp-web-scraper.git
cd mcp-web-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

Server runs at `http://localhost:8000/mcp`

### Test Locally

```bash
# List tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Test web search
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"web_search",
      "arguments":{"query":"AI news","max_results":3}
    }
  }'
```

## 🛠️ Adding New Tools

### 1. Search Tool Example

Edit `tools/search.py`:

```python
@mcp.tool()
def my_custom_search(query: str) -> dict:
    """Your custom search tool"""
    # Implementation here
    return {"success": True, "data": []}
```

### 2. Scraping Tool Example

Edit `tools/scraping.py`:

```python
@mcp.tool()
def my_custom_scraper(url: str) -> dict:
    """Your custom scraper"""
    # Implementation here
    return {"success": True, "content": ""}
```

### 3. Deploy Changes

```bash
git add .
git commit -m "Add new tools"
git push origin main
# Render auto-deploys!
```

## 📊 Monitoring

### View Logs
1. Render Dashboard → Your Service
2. Click **"Logs"** tab
3. View real-time logs

### Health Check
```bash
curl https://your-app.onrender.com/health
```

## 🎯 Architecture Benefits

### ✅ Modular Design
- **Separation of concerns** - Each file has one responsibility
- **Easy to maintain** - Find and update code quickly
- **Scalable** - Add new tools without touching existing code

### ✅ Clean Code
- **Type hints** - Better IDE support and error catching
- **Logging** - Track all operations
- **Error handling** - Graceful failures with detailed errors

### ✅ Production Ready
- **Official MCP SDK** - FastMCP framework
- **Streamable HTTP** - Single endpoint communication
- **Stateless** - Horizontally scalable
- **Health checks** - Automatic monitoring

## 💬 Example Usage in Claude

- "Search for latest quantum computing news"
- "Extract the article from https://example.com/post"
- "Find and scrape top 5 articles about AI safety"
- "Get all links from https://news.ycombinator.com"
- "Do comprehensive research on renewable energy"

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure you're in project root
cd mcp-web-scraper

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run server
python server.py
```

### Tools Not Registered
Check logs for "Registering X tools..." messages

### Module Not Found
Ensure all `__init__.py` files exist in:
- `tools/__init__.py`
- `utils/__init__.py`

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP](https://gofastmcp.com/)
- [Render Docs](https://render.com/docs)

## 📄 License

MIT License - Free to use and modify!

---

**Modular** ✅ | **Production-Ready** ✅ | **Easy to Extend** ✅