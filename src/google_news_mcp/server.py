
from mcp.server import MCPServer

from google_news_mcp.services.news_service import NewsService
from google_news_mcp.tools.news_tools import register_news_tools
from google_news_mcp.resources.news_resources import register_news_resources
from google_news_mcp.prompts.news_prompts import register_news_prompts


mcp = MCPServer("Google News MCP")

news_service = NewsService()

# Register MCP tools
register_news_tools(mcp, news_service)
register_news_prompts(mcp)

# Register MCP resources
register_news_resources(mcp)


if __name__ == "__main__":
    mcp.run()
