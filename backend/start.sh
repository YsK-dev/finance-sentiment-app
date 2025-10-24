#!/bin/bash
# Start script for Render deployment

# Set PYTHONPATH to the current directory (backend) so Python can find the app module
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Debug: Show where we are and what's in the directory
echo "Current directory: $(pwd)"
echo "Contents:"
ls -la

# Port is provided by Render as $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
