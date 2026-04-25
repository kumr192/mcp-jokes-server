"""Tiny custom MCP client. Connects with Basic Auth, lists tools, calls each.

Usage:
    pip install mcp
    export MCP_URL=https://your-app.up.railway.app/mcp
    export MCP_USERNAME=admin
    export MCP_PASSWORD=change-me
    python client_example.py
"""
import asyncio
import base64
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main() -> None:
    url = os.environ.get("MCP_URL", "http://localhost:8000/mcp")
    username = os.environ["MCP_USERNAME"]
    password = os.environ["MCP_PASSWORD"]
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}

    async with streamablehttp_client(url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            joke = await session.call_tool("adult_joke", {})
            print("\nadult_joke ->", joke.content[0].text)

            rnd = await session.call_tool("genz_word", {})
            print("\ngenz_word (random) ->", rnd.content[0].text)

            specific = await session.call_tool("genz_word", {"word": "rizz"})
            print("\ngenz_word(rizz) ->", specific.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
