#!/bin/bash
# Build script for Render deployment

set -e  # Exit on error

echo "Installing dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "Backend build completed successfully!"
