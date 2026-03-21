#!/usr/bin/env bash
set -euo pipefail

echo "== git status --short =="
git status --short || true

echo
if git remote -v >/dev/null 2>&1; then
  echo "== git remote -v =="
  git remote -v || true
fi
