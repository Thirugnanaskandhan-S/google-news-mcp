from pathlib import Path

from mcp.server import MCPServer

from google_news_mcp.apps.news_app import apps
from google_news_mcp.prompts.news_prompts import register_news_prompts
from google_news_mcp.resources.news_resources import register_news_resources
from google_news_mcp.services.gemini_service import GeminiNewsAnalyst
from google_news_mcp.services.news_service import NewsService
from google_news_mcp.tools.gemini_tools import register_gemini_tools
from google_news_mcp.tools.news_tools import register_news_tools

# Load GEMINI_API_KEY / GEMINI_MODEL from the project's .env (optional dependency).
try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")


mcp = MCPServer(
    "Google News MCP",
    extensions=[apps],
    # Extra packages `mcp dev` installs when it launches this server.
    dependencies=["google-genai", "python-dotenv"],
)

news_service = NewsService()

# Register MCP tools
register_news_tools(mcp, news_service)
register_gemini_tools(mcp, GeminiNewsAnalyst(mcp))
register_news_prompts(mcp)

# Register MCP resources
register_news_resources(mcp)


if __name__ == "__main__":
    mcp.run()
