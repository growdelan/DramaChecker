#!/usr/bin/env bash
set -euo pipefail

echo "== git status --short =="
git status --short || true

echo
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "== recently changed files =="
  git diff --name-only HEAD || true
fi
