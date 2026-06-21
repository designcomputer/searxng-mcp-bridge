# searxng-mcp-bridge

A minimal [MCP](https://modelcontextprotocol.io/) server that exposes a private
[SearXNG](https://github.com/searxng/searxng) instance as a `search` tool over
**streamable-HTTP**, so it can be used as a web-search tool from the
[llama.cpp](https://github.com/ggml-org/llama.cpp) WebUI (or any MCP client that
speaks streamable-HTTP / SSE).

It is deliberately tiny — one file, two dependencies (`fastmcp`, `httpx`) — as an
auditable alternative to heavier SearXNG MCP packages.

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
