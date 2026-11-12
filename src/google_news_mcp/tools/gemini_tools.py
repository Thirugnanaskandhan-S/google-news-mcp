from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from google_news_mcp.models.analysis import NewsAnalysisResponse
from google_news_mcp.services.gemini_service import (
    GeminiConfigurationError,
    GeminiNewsAnalyst,
)


def register_gemini_tools(
    mcp: MCPServer,
    analyst: GeminiNewsAnalyst,
) -> None:
    """Register the Gemini-powered news analysis tool with the MCP server."""

    @mcp.tool()
    async def analyze_news_with_gemini(
        question: Annotated[
            str,
            Field(
                min_length=2,
                max_length=300,
                description=(
                    "A natural-language news question, such as "
                    "'Find the latest AI infrastructure news from BBC'."
                ),
            ),
        ],
        ctx: Context,
    ) -> NewsAnalysisResponse:
        """Answer a news question with Gemini.

        Gemini chooses which Google News tools to call, then writes a short briefing
        based only on the returned articles. The articles in the response are the
        original Google News results.
        """

        step = 0

        async def report(message: str) -> None:
            # Progress notifications reach clients that sent a progress token.
            nonlocal step
            step += 1
            await ctx.report_progress(step, message=message)

        try:
            return await analyst.analyze(question, on_progress=report)
        except GeminiConfigurationError as error:
            raise ToolError(str(error)) from error
        except Exception as error:
            raise ToolError(f"Gemini analysis failed: {error}") from error
