#!/usr/bin/env python3
"""Minimal MCP server bridging SearXNG's JSON API to MCP tools.

Serves streamable-HTTP so the llama.cpp WebUI (browser MCP client) can use it.
Config via env:
  SEARXNG_URL   base URL of the SearXNG instance (default http://127.0.0.1:4000)
  HOST          bind address (default 0.0.0.0)
  PORT          listen port (default 8000)
  MCP_PATH      HTTP path for the MCP endpoint (default /mcp)
"""

import os

import httpx
from fastmcp import FastMCP

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:4000").rstrip("/")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")

mcp = FastMCP("searxng")


@mcp.tool()
def search(
    query: str,
    max_results: int = 10,
    categories: str | None = None,
    language: str | None = None,
    time_range: str | None = None,
) -> list[dict]:
    """Search the web via a private SearXNG instance.

    Args:
        query: The search query.
        max_results: Maximum number of results to return (default 10).
        categories: Comma-separated SearXNG categories, e.g. "general", "news",
            "science", "it". Omit for the default.
        language: Language code such as "en" or "en-US". Omit for any.
        time_range: One of "day", "week", "month", "year". Omit for any time.

    Returns:
        A list of results, each with title, url, content (snippet), and engine.
    """
    params: dict[str, str] = {"q": query, "format": "json"}
    if categories:
        params["categories"] = categories
    if language:
        params["language"] = language
    if time_range:
        params["time_range"] = time_range

    resp = httpx.get(f"{SEARXNG_URL}/search", params=params, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for r in data.get("results", [])[:max_results]:
        results.append(
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
                "engine": r.get("engine"),
            }
        )
    return results


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=HOST, port=PORT, path=MCP_PATH)
