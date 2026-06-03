#!/usr/bin/env bash
set -euo pipefail

# Prepare an Ubuntu GPU machine for EvoScientist reproduction runs.
# Intended to be run from the repository root on the Ubuntu host.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${EVOSCI_CONDA_ENV:-evoscientist-repro}"
PYTHON_VERSION="${EVOSCI_PYTHON_VERSION:-3.11}"

cd "$ROOT"

if [ -f "$HOME/.codex/env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.codex/env"
  set +a
fi

echo "== Host =="
hostname
uname -a

echo "== GPU =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
  echo "nvidia-smi not found"
fi

if ! command -v conda >/dev/null 2>&1; then
  if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    # shellcheck disable=SC1091
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
  else
    echo "conda is required but was not found." >&2
    exit 2
  fi
fi

if ! conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  echo "Creating conda env: $ENV_NAME (python=$PYTHON_VERSION)"
  conda create -y -n "$ENV_NAME" "python=$PYTHON_VERSION"
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

python --version
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]'

.venv/bin/python --version >/dev/null 2>&1 || true

python - <<'PY'
import os
for key in ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "MONICA_API_KEY", "MONICA_BASE_URL"]:
    print(f"{key}={'SET' if os.environ.get(key) else '(not set)'}")
PY

python -m EvoScientist config set provider deepseek
python -m EvoScientist config set model deepseek-v4-flash
python -m EvoScientist config set enable_async_subagents false

echo "== EvoScientist config =="
python -m EvoScientist config get provider
python -m EvoScientist config get model
python -m EvoScientist config get enable_async_subagents

echo "Ubuntu GPU setup complete."
