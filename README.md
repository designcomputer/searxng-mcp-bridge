# searxng-mcp-bridge

A minimal [MCP](https://modelcontextprotocol.io/) server that exposes a private
[SearXNG](https://github.com/searxng/searxng) instance as a `search` tool over
**streamable-HTTP**, so it can be used as a web-search tool from the
[llama.cpp](https://github.com/ggml-org/llama.cpp) WebUI (or any MCP client that
speaks streamable-HTTP / SSE).

It is deliberately tiny — one file, two dependencies (`fastmcp`, `httpx`) — as an
auditable alternative to heavier SearXNG MCP packages.

## Why this exists

There are existing SearXNG MCP servers, so why another one? Two reasons specific
to this use case:

- **Transport.** The llama.cpp WebUI is a browser-based MCP client, so it can
  only talk to MCP servers over a network transport (streamable-HTTP / SSE /
  WebSocket) — not stdio. Many published SearXNG MCP servers are stdio-first
  (aimed at Claude Desktop / IDEs), which doesn't fit here.
- **Footprint.** This service runs unauthenticated on the local network, so its
  dependency and supply-chain surface matters. The most prominent PyPI option
  (`searxng-mcp`) pulls in **~167 transitive packages** — including `litellm`,
  `llama-index-core`, `confluent-kafka`, and a number of the author's own
  utility packages — for what is ultimately a thin wrapper around one HTTP
  endpoint. That's a lot of unrelated code to trust and keep updated.

Since the actual job is trivial (forward a query to SearXNG's JSON API and return
the results), a single readable file with two well-known dependencies is easier
to audit, deploy, and reason about than adopting a large general-purpose package.

## How it works

```
llama.cpp WebUI (browser MCP client)
        │  streamable-HTTP  http://<host>:8000/mcp
        ▼
   server.py  (this bridge)
        │  GET /search?format=json
        ▼
   SearXNG  http://127.0.0.1:4000
```

The WebUI's MCP client is browser-based and only supports network transports
(streamable-HTTP / SSE / WebSocket) — not stdio — which is why this bridge serves
HTTP.

## Tool

`search(query, max_results=10, categories=None, language=None, time_range=None)`
— returns a list of `{title, url, content, engine}` from SearXNG.

## Configuration (env vars)

| Var           | Default                  | Meaning                         |
|---------------|--------------------------|---------------------------------|
| `SEARXNG_URL` | `http://127.0.0.1:4000`  | Base URL of the SearXNG instance |
| `HOST`        | `0.0.0.0`                | Bind address                    |
| `PORT`        | `8000`                   | Listen port                     |
| `MCP_PATH`    | `/mcp`                   | HTTP path for the MCP endpoint  |

SearXNG must have the JSON format enabled (`search.formats` includes `json` in
`settings.yml`).

## Install (systemd)

```bash
git clone <this-repo> /opt/searxng-mcp
cd /opt/searxng-mcp
./install.sh            # creates .venv, installs the unit, enables + starts it
```

`install.sh` rewrites the unit's paths/user to wherever the repo lives. Override
the interpreter or service user with `PYTHON=`, `SERVICE_USER=`, `SERVICE_GROUP=`.

Manage it:

```bash
sudo systemctl restart searxng-mcp
journalctl -u searxng-mcp -f
```

## Run manually (dev)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
SEARXNG_URL=http://127.0.0.1:4000 .venv/bin/python server.py
```

## Wire into the llama.cpp WebUI

In **WebUI → MCP Servers**, add a server with transport **Streamable HTTP** and
URL `http://<host>:8000/mcp`. Use a tool-capable model served with `--jinja`.

## Security note

Binding `HOST=0.0.0.0` exposes an unauthenticated search endpoint on every
reachable network (LAN/VPN). Use `127.0.0.1` if you only need local access, or
restrict at the firewall.

## License

[MIT](LICENSE)
