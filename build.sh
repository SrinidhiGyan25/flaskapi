#!/usr/bin/env bash
set -e

echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🌐 Setting up Chrome for Render..."
# Render provides Chrome in their environment
# Just need to install chromedriver-binary via pip

echo "🎉 Build completed successfully!"