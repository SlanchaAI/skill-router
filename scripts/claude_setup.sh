#!/bin/sh
set -eu

MODE=setup
case "${1:-}" in
  "") ;;
  --doctor) MODE=doctor ;;
  --repair) MODE=repair ;;
  *) echo "usage: $0 [--doctor|--repair]" >&2; exit 2 ;;
esac

MCP_URL=${INGOT_MCP_URL:-http://localhost:8000/mcp}
LF_URL=${LANGFUSE_BASE_URL:-http://localhost:3100}
trap 'echo "error: Claude setup failed; run $0 --doctor for diagnostics or $0 --repair to reinstall managed state" >&2' 0

command -v claude >/dev/null 2>&1 || { echo "error: Claude Code is not installed" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "error: Python 3.9 or newer is required" >&2; exit 1; }
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' || {
  echo "error: Python 3.9 or newer is required by the Langfuse plugin" >&2
  exit 1
}

MCP_DETAILS=$(claude mcp get ingot 2>/dev/null || true)
MCP_OK=0
printf '%s' "$MCP_DETAILS" | grep -F "$MCP_URL" >/dev/null 2>&1 && MCP_OK=1
MARKETPLACE_OK=0
claude plugin marketplace list --json 2>/dev/null | grep -F 'langfuse-observability' >/dev/null && MARKETPLACE_OK=1
PLUGIN_OK=0
claude plugin list --json 2>/dev/null | grep -F 'langfuse-observability@langfuse-observability' >/dev/null && PLUGIN_OK=1
SDK_OK=0
python3 -c 'import importlib.metadata as m; v=m.version("langfuse"); raise SystemExit(v.split(".")[0] != "4")' \
  >/dev/null 2>&1 && SDK_OK=1

if [ "$MODE" = "doctor" ]; then
  echo "Claude Code version: $(claude --version)"
  echo "Python version: $(python3 --version)"
  [ "$MCP_OK" = "1" ] && echo "Ingot MCP: configured at $MCP_URL" || echo "Ingot MCP: missing or URL mismatch"
  [ "$MARKETPLACE_OK" = "1" ] && echo "Langfuse marketplace: installed" || echo "Langfuse marketplace: missing"
  [ "$PLUGIN_OK" = "1" ] && echo "Langfuse plugin: installed" || echo "Langfuse plugin: missing"
  [ "$SDK_OK" = "1" ] && echo "Langfuse Python SDK: compatible 4.x" || echo "Langfuse Python SDK: missing or incompatible"
  if command -v curl >/dev/null 2>&1 && curl -sSf "$LF_URL/api/public/health" >/dev/null 2>&1; then
    echo "Langfuse endpoint: healthy at $LF_URL"
  else
    echo "Langfuse endpoint: unreachable at $LF_URL"
  fi
  trap - 0
  [ "$MCP_OK" = "1" ] && [ "$MARKETPLACE_OK" = "1" ] && [ "$PLUGIN_OK" = "1" ] && [ "$SDK_OK" = "1" ]
  exit
fi

if [ "$MCP_OK" != "1" ]; then
  if [ -n "$MCP_DETAILS" ]; then
    if [ "$MODE" = "repair" ]; then
      claude mcp remove --scope user ingot
    else
      echo "error: Ingot MCP exists with a different URL; run $0 --repair" >&2
      exit 1
    fi
  fi
  claude mcp add --scope user --transport http ingot "$MCP_URL"
else
  echo "Ingot MCP is already configured at $MCP_URL."
fi

if [ "$SDK_OK" != "1" ] || [ "$MODE" = "repair" ]; then
  python3 -m pip install --user --upgrade 'langfuse>=4.0,<5'
else
  echo "Langfuse Python SDK 4.x is already installed."
fi
if [ "$MARKETPLACE_OK" != "1" ]; then
  claude plugin marketplace add langfuse/Claude-Observability-Plugin
fi
if [ "$MODE" = "repair" ] && [ "$PLUGIN_OK" = "1" ]; then
  claude plugin uninstall --scope user --yes langfuse-observability@langfuse-observability
  PLUGIN_OK=0
fi
if [ "$PLUGIN_OK" != "1" ]; then
  claude plugin install --scope user langfuse-observability@langfuse-observability
else
  echo "Langfuse observability plugin is already installed."
fi

trap - 0
echo "Claude Code setup complete."
echo "Restart Claude Code and enter your Langfuse URL and project keys when the plugin prompts."
echo "For the bundled stack use http://localhost:3100 and the keys from docker-compose.yml."
echo "Ask Claude to call ingot.route_and_load once at the start of each request."
