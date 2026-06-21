#!/usr/bin/env bash
# Install the SearXNG MCP bridge as a systemd service.
# Run from the repo directory: sudo ./install.sh  (re-runnable / idempotent)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-/usr/bin/python3}"   # system python; avoids a broken uv toolchain

echo "==> Creating venv at $REPO_DIR/.venv (using $PYTHON)"
"$PYTHON" -m venv "$REPO_DIR/.venv"
"$REPO_DIR/.venv/bin/pip" install --upgrade pip >/dev/null
"$REPO_DIR/.venv/bin/pip" install -r "$REPO_DIR/requirements.txt"

echo "==> Installing systemd unit"
# Patch the unit's paths/user to wherever the repo actually lives.
sed -e "s#^WorkingDirectory=.*#WorkingDirectory=$REPO_DIR#" \
    -e "s#^ExecStart=.*#ExecStart=$REPO_DIR/.venv/bin/python $REPO_DIR/server.py#" \
    -e "s#^User=.*#User=${SERVICE_USER:-$(id -un)}#" \
    -e "s#^Group=.*#Group=${SERVICE_GROUP:-$(id -gn)}#" \
    "$REPO_DIR/searxng-mcp.service" | sudo tee /etc/systemd/system/searxng-mcp.service >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable --now searxng-mcp.service

echo "==> Done. Status:"
systemctl --no-pager --full status searxng-mcp.service | head -8
