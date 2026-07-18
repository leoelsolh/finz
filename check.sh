#!/usr/bin/env bash
set -e
ruff check .
pytest test_app.py
