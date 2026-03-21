#!/usr/bin/env bash
set -euo pipefail

echo "== git status --short =="
git status --short || true

echo
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "== changed files vs HEAD =="
  git diff --name-only HEAD || true
else
  echo "== repository has no commits yet; listing tracked files =="
  git ls-files || true
fi
