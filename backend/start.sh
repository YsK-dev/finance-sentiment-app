#!/bin/bash
# Start script for Render deployment

# Port is provided by Render as $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
