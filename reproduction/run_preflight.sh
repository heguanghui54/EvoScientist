#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f "$HOME/.codex/env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.codex/env"
  set +a
fi

BUNDLED_PY="/Users/hgh54913/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  if [[ -x "$BUNDLED_PY" ]]; then
    PY="$BUNDLED_PY"
  else
    PY="$(command -v python3 || true)"
  fi
fi

if [[ ! -x "$PY" ]]; then
  echo "Python executable not found: $PY" >&2
  exit 1
fi

if [[ -d .venv && ! -x .venv/bin/EvoSci ]]; then
  echo "Existing .venv is missing EvoSci; rebuilding it."
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip setuptools wheel
if ! .venv/bin/python -m pip show EvoScientist >/dev/null 2>&1; then
  .venv/bin/python -m pip install -e '.[dev]'
fi

.venv/bin/EvoSci --help >/tmp/evosci_help.txt

.venv/bin/python - <<'PY'
from EvoScientist import EvoScientist_agent
from EvoScientist.config.settings import load_config

print("agent_import_ok")
print(type(EvoScientist_agent).__name__)
print("config_ok", type(load_config()).__name__)
PY

.venv/bin/python -m pytest \
  tests/test_config.py \
  tests/test_paths.py \
  tests/test_prompts.py \
  tests/test_stream_utils.py \
  -q --timeout=30

if [[ "${1:-}" == "--with-agent" ]]; then
  .venv/bin/EvoSci \
    -p "Run a tiny EvoScientist reproduction smoke test: summarize the local setup and name one next experiment. Do not execute shell commands." \
    --ui cli --auto-mode --no-thinking
fi
