"""Streamlit test page for the jokes-and-genz MCP server.

Usage:
    uv run streamlit run streamlit_app.py
"""
from __future__ import annotations

import asyncio
import json
import os

import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

DEFAULT_URL = os.environ.get(
    "MCP_URL",
    "https://web-production-3a648.up.railway.app/mcp",
)


async def _list_tools(url: str) -> list:
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return (await session.list_tools()).tools


async def _call_tool(url: str, name: str, args: dict):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(name, args)


def _text_of(result) -> str:
    if not result.content:
        return ""
    return getattr(result.content[0], "text", str(result.content[0]))


st.set_page_config(page_title="MCP Tester", page_icon="🎲", layout="centered")
st.title("🎲 MCP Tester — jokes-and-genz")
st.caption("Calls the public MCP server over Streamable HTTP.")

with st.sidebar:
    st.header("Connection")
    url = st.text_input("MCP server URL", value=DEFAULT_URL)
    if st.button("Connect & list tools", use_container_width=True):
        try:
            tools = asyncio.run(_list_tools(url))
            st.success(f"Connected — {len(tools)} tool(s):")
            for t in tools:
                st.markdown(f"- **`{t.name}`** — {t.description or ''}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

st.subheader("adult_joke")
st.caption("Random PG-13 joke. No arguments.")
if st.button("🃏 Get a joke"):
    try:
        result = asyncio.run(_call_tool(url, "adult_joke", {}))
        st.success(_text_of(result))
    except Exception as e:
        st.error(str(e))

st.divider()

st.subheader("genz_word")
st.caption("Look up a slang word, or leave blank for a random one.")
word = st.text_input("Word (optional)", placeholder="e.g. rizz, bussin, mid")
if st.button("🔤 Look up"):
    try:
        args = {"word": word.strip()} if word.strip() else {}
        result = asyncio.run(_call_tool(url, "genz_word", args))
        text = _text_of(result)
        try:
            st.json(json.loads(text))
        except json.JSONDecodeError:
            st.write(text)
    except Exception as e:
        st.error(str(e))
