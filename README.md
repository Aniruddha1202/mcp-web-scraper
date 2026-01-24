🚀 MCP Web Scraper Server
A production-ready MCP (Model Context Protocol) server for advanced web scraping and search, easily deployable on Railway.

✨ Features
🔍 Advanced Web Search - Search anything on the web using DuckDuckGo
🤖 Smart Search - Intelligent search with quick/standard/comprehensive modes
📰 News Search - Dedicated news article search with dates and sources
🎯 Search & Scrape - Automatically search and extract full content from results
📄 Article Extraction - Clean article content extraction (removes ads/navigation)
🔗 Link Extraction - Extract all links with regex filtering
📊 Table Extraction - Extract table data from webpages
📝 Metadata Extraction - Get page metadata and Open Graph tags
🚀 Easy Railway Deployment
💪 Production-ready
🛠️ Tools Available
🔍 Search Tools
web_search - Search the web for anything (just give a query!)
smart_search - Intelligent search with modes (quick/standard/comprehensive)
search_and_scrape - Search + automatically scrape full content
news_search - Search specifically for news articles
📄 Scraping Tools
scrape_html - Scrape HTML content with optional CSS selectors
extract_links - Extract all links with optional filtering
extract_metadata - Get page metadata and Open Graph tags
scrape_table - Extract table data from webpages
extract_article - Clean article extraction (removes ads/navigation)
🚀 Quick Deploy to Railway
Step 1: Create GitHub Repository
bash
# Clone or download this repository
git clone https://github.com/yourusername/mcp-web-scraper.git
cd mcp-web-scraper

# Or create new repository
mkdir mcp-web-scraper
cd mcp-web-scraper
# Copy all files here

# Initialize git
git init
git add .
git commit -m "Initial commit: MCP Web Scraper Server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mcp-web-scraper.git
git push -u origin main
Step 2: Deploy to Railway
Go to railway.app
Click "New Project"
Select "Deploy from GitHub repo"
Choose your repository
Railway automatically detects Dockerfile and deploys! 🎉
Step 3: Get Your URL
Click on your deployment in Railway
Go to "Settings" → "Domains"
Click "Generate Domain"
Copy your URL (e.g., https://mcp-web-scraper-production.up.railway.app)
Step 4: Test Your Server
bash
# Health check
curl https://your-app.up.railway.app/health

# List available tools
curl https://your-app.up.railway.app/tools

# Test web search
curl -X POST https://your-app.up.railway.app/call-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "web_search", "arguments": {"query": "latest AI news"}}'
💻 Local Development
bash
# Clone repository
git clone https://github.com/yourusername/mcp-web-scraper.git
cd mcp-web-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.server:app --reload --port 8000
Visit http://localhost:8000 to see the server running!

🔌 Connect to Claude Desktop
Add to your Claude Desktop config (claude_desktop_config.json):

macOS: ~/Library/Application Support/Claude/claude_desktop_config.json Windows: %APPDATA%\Claude\claude_desktop_config.json

json
{
  "mcpServers": {
    "web-scraper": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://your-app.up.railway.app/sse"
      ]
    }
  }
}
Then restart Claude Desktop!

📋 Example Usage
Search the Web
bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "arguments": {
      "query": "best pizza recipe",
      "max_results": 5
    }
  }'
Smart Search (Comprehensive)
bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "smart_search",
    "arguments": {
      "query": "climate change solutions",
      "mode": "comprehensive"
    }
  }'
Search and Scrape
bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_and_scrape",
    "arguments": {
      "query": "machine learning tutorials",
      "num_results": 3
    }
  }'
News Search
bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "news_search",
    "arguments": {
      "query": "technology",
      "max_results": 10
    }
  }'
Extract Article
bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "extract_article",
    "arguments": {
      "url": "https://example.com/article"
    }
  }'
🎯 Use Cases in Claude
Once connected, you can ask Claude:

"Search for the best Italian restaurants in Rome"
"Find me recent articles about quantum computing"
"What's the latest news on AI developments?"
"Research blockchain technology and give me detailed info"
"Scrape the table from this webpage: [URL]"
"Extract all links from example.com"
📁 Project Structure
mcp-web-scraper/
├── src/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # FastAPI server and MCP integration
│   └── tools.py          # Web scraping and search tools
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── railway.json          # Railway deployment config
├── .gitignore            # Git ignore file
└── README.md             # This file
🔧 Configuration
Environment Variables (Optional)
You can set these in Railway dashboard under "Variables":

LOG_LEVEL - Logging level (default: INFO)
PORT - Server port (default: 8000)
HOST - Server host (default: 0.0.0.0)
📊 Monitoring
Railway provides built-in monitoring:

Metrics - CPU, Memory, Network usage
Logs - Real-time application logs
Deployments - Deployment history and rollbacks
Access these in your Railway dashboard.

💰 Cost
Railway Free Tier:

$5 free credit per month
500 hours of usage
Perfect for personal use and testing
For production use, consider upgrading to Railway Pro.

🔒 Security Notes
⚠️ This server is deployed without authentication for easy use. For production:

Consider adding API key authentication
Implement rate limiting
Restrict allowed domains
Use environment variables for sensitive data
🐛 Troubleshooting
Server not starting?
Check Railway logs in dashboard
Verify all files are committed to Git
Ensure Dockerfile is in root directory
Tools not working?
Check tool names match exactly
Verify JSON format in requests
Check server logs for errors
Can't connect to Claude?
Verify Railway URL is correct
Ensure /sse endpoint is accessible
Restart Claude Desktop after config change
🤝 Contributing
Contributions are welcome! Feel free to:

Report bugs
Suggest new features
Submit pull requests
📄 License
MIT License - feel free to use and modify!

🙏 Acknowledgments
Built with:

FastAPI - Web framework
MCP - Model Context Protocol
DuckDuckGo Search - Web search
Trafilatura - Content extraction
BeautifulSoup - HTML parsing
Railway - Deployment platform
📞 Support
GitHub Issues: Report a bug
Railway Docs: docs.railway.app
MCP Docs: modelcontextprotocol.io
Made with ❤️ for the MCP community

