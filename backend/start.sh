#!/bin/bash
# Start script for Render deployment

# Ensure we're in the backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set PYTHONPATH to the current directory so Python can find the app module
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"

# Debug: Show where we are and what's in the directory
echo "==== Deployment Debug Info ===="
echo "Script directory: $SCRIPT_DIR"
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"
echo "Contents of current directory:"
ls -la
echo "Contents of app directory:"
ls -la app/
echo "Contents of app/models directory:"
ls -la app/models/
echo "=============================="

# Port is provided by Render as $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
