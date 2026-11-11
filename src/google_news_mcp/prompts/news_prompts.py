
from mcp.server import MCPServer


def register_news_prompts(mcp: MCPServer) -> None:
    """Register reusable Google News prompts."""

    @mcp.prompt()
    def daily_news_briefing(
        region: str = "India",
        focus: str = "Technology, Business and World News",
    ) -> str:
        """Create instructions for a daily news briefing."""

        return f"""
        Prepare a daily news briefing for {region}.

        Focus areas: {focus}.

        Organize the briefing into clear sections.

        For each important story:
        - Explain what happened.
        - Explain why it matters.
        - Include the publisher and publication date.
        - Include the original article URL.

        Prioritize factual reporting.
        Clearly distinguish confirmed facts from speculation.
        """

    @mcp.prompt()
    def summarize_news(
        articles: str,
        style: str = "concise",
    ) -> str:
        """Generate instructions to summarize news articles."""

        return f"""
        Summarize the following news articles.

        Summary style: {style}.

        Instructions:
        - Identify the main event.
        - Explain the important facts.
        - Highlight important names, organizations and dates.
        - Avoid repeating information.
        - Do not invent missing information.
        - Preserve article source references.

        Articles:
        {articles}
        """

    @mcp.prompt()
    def compare_publishers(
        topic: str,
        publisher_a: str,
        publisher_b: str,
    ) -> str:
        """Generate instructions to compare two publishers' coverage."""

        return f"""
        Compare how two publishers cover the following topic.

        Topic: {topic}

        Publisher A: {publisher_a}
        Publisher B: {publisher_b}

        Analyze:
        - Main angle of each publisher.
        - Facts emphasized by each publisher.
        - Differences in framing and perspective.
        - Information common to both reports.
        - Information reported by only one publisher.

        Do not assume that differences in coverage indicate bias.
        Distinguish factual differences from differences in emphasis.
        """
