import os
import sys

_KEY_HELP = """\
error: OPENROUTER_API_KEY is not set — the optimizer needs it for LLM calls.

  1. cp .env.example .env
  2. put your key in it (get one at https://openrouter.ai/keys)
  3. re-run this command
"""


def require_openrouter_key() -> None:
    """Friendly preflight for the CLI entrypoints: exit with setup help instead of a mid-run 401."""
    if not os.environ.get("OPENROUTER_API_KEY", "").strip():
        print(_KEY_HELP, file=sys.stderr)
        raise SystemExit(1)
