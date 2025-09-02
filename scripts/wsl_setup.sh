#!/usr/bin/env bash

set -euo pipefail

echo "🚧 WSL setup: preparing Python environment..."

# Pick python executable
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

# Create venv if missing OR if it's a Windows venv (no bin/activate)
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
  if [ -d ".venv" ] && [ ! -f ".venv/bin/activate" ]; then
    echo "♻️  Detected non-Linux virtualenv structure (.venv without bin/activate). Recreating..."
    rm -rf .venv
  fi
  echo "📦 Creating virtual environment (.venv)..."
  "$PY" -m venv .venv
fi

echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "⬆️  Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "📥 Installing backend requirements..."
if [ -f "backend/requirements.txt" ]; then
  pip install -r backend/requirements.txt
fi

if [ -f "backend/requirements-dev.txt" ]; then
  echo "📥 Installing dev requirements (excluding editable installs)..."
  # Exclude '-e .' which requires a pyproject.toml/setup.py at repo root
  TMP_DEV_REQS=$(mktemp)
  grep -v -E '^\s*-e\s+\.' backend/requirements-dev.txt > "$TMP_DEV_REQS" || true
  if [ -s "$TMP_DEV_REQS" ]; then
    pip install -r "$TMP_DEV_REQS"
  else
    echo "(no dev requirements to install)"
  fi
  rm -f "$TMP_DEV_REQS"
fi

echo "⚙️  Ensuring .env exists..."
if [ ! -f "backend/.env" ] && [ -f "backend/env.example" ]; then
  cp backend/env.example backend/.env
  echo "Created backend/.env from template. Update secrets if needed."
fi

echo "📁 Ensuring backend data/logs directories exist..."
mkdir -p backend/data/raw backend/data/processed backend/data/samples backend/logs

echo "✅ WSL setup complete."
echo "Next steps:"
echo "  1) source .venv/bin/activate"
echo "  2) ./scripts/run_dev.sh  # or: make dev"
