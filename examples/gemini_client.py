import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import Client as MCPClient
from mcp import StdioServerParameters


load_dotenv()

MAX_TOOL_ROUNDS = 5


def convert_mcp_tools_to_gemini(mcp_tools):
    """Convert MCP tool definitions into Gemini function declarations."""
    declarations = []

    for tool in mcp_tools:
        declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or tool.name,
                parameters_json_schema=tool.input_schema,
            )
        )

    return [types.Tool(function_declarations=declarations)]


def serialize_mcp_result(result) -> dict:
    """Convert MCP results into JSON-compatible data."""
    if result.structured_content is not None:
        return result.structured_content

    content = []
    for item in result.content:
        if hasattr(item, "text"):
            content.append(item.text)

    return {
        "content": content,
        "is_error": result.is_error,
    }


async def main() -> None:
    """Run a multi-step Gemini and MCP tool-calling workflow."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "google_news_mcp.server"],
    )

    async with MCPClient(server) as mcp_client:
        print("Connected to Google News MCP.")

        # 1. Discover available MCP tools.
        mcp_result = await mcp_client.list_tools()
        available_tools = {tool.name for tool in mcp_result.tools}
        gemini_tools = convert_mcp_tools_to_gemini(mcp_result.tools)

        print(f"Discovered {len(available_tools)} tools.")

        # 2. Initialize Gemini.
        async with genai.Client(api_key=api_key).aio as gemini_client:
            prompt = (
                "Find five recent articles about AI infrastructure "
                "published by BBC. Use the appropriate available "
                "Google News tool. Do not invent article details."
            )
            print("\nUser:", prompt)

            # 3. Preserve the complete conversation history.
            conversation = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ]

            config = types.GenerateContentConfig(
                tools=gemini_tools,
                temperature=0.2,
            )

            response = await gemini_client.models.generate_content(
                model=model,
                contents=conversation,
                config=config,
            )

            # 4. Execute Gemini-requested tools.
            tool_round = 0

            while response.function_calls:
                tool_round += 1
                if tool_round > MAX_TOOL_ROUNDS:
                    raise RuntimeError(
                        f"Maximum tool rounds ({MAX_TOOL_ROUNDS}) reached."
                    )

                print(f"\nTool execution round: {tool_round}")

                if not response.candidates:
                    raise RuntimeError("Gemini returned no response candidate.")

                model_content = response.candidates[0].content
                if model_content is None:
                    raise RuntimeError("Gemini returned an empty response.")

                # Keep Gemini's function-call message in the conversation.
                conversation.append(model_content)
                function_response_parts = []

                for function_call in response.function_calls:
                    tool_name = function_call.name
                    arguments = dict(function_call.args or {})

                    if tool_name not in available_tools:
                        raise RuntimeError(
                            f"Unknown MCP tool requested: {tool_name}"
                        )

                    print(f"\nGemini selected: {tool_name}")
                    print("Arguments:", arguments)

                    try:
                        tool_result = await mcp_client.call_tool(
                            tool_name,
                            arguments,
                        )
                        result_data = serialize_mcp_result(tool_result)

                        if tool_result.is_error:
                            result_data = {"error": result_data}
                    except Exception as error:
                        result_data = {"error": str(error)}

                    print("MCP execution completed.")

                    # Build the response object; the optional call ID helps
                    # correlate the result with Gemini's requested function.
                    function_response = types.FunctionResponse(
                        name=tool_name,
                        response=result_data,
                        id=function_call.id,
                    )
                    function_response_parts.append(
                        types.Part(function_response=function_response)
                    )

                # Gemini's current API endpoint rejects role="tool" here.
                # The function response is sent as a user content turn.
                conversation.append(
                    types.Content(
                        role="user",
                        parts=function_response_parts,
                    )
                )

                # 5. Ask Gemini to continue with the full conversation.
                response = await gemini_client.models.generate_content(
                    model=model,
                    contents=conversation,
                    config=config,
                )

            # 6. Display Gemini's final answer.
            print("\n" + "=" * 55)
            print("GEMINI FINAL ANSWER")
            print("=" * 55)
            print(response.text or "Gemini returned no text answer.")
            print(f"\nTotal tool execution rounds: {tool_round}")


if __name__ == "__main__":
    asyncio.run(main())
