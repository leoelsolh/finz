#!/usr/bin/env bash
echo "Running Ruff..."
set -e
ruff check .
echo
echo "Running Pytest Suite..."
pytest test_app.py -v
