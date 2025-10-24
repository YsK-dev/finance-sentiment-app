#!/usr/bin/env python3
"""
Wrapper script to ensure proper Python path before starting the FastAPI app.
This must be run from the backend directory.
"""
import sys
import os
from pathlib import Path

# Get the absolute path to the backend directory
backend_dir = Path(__file__).parent.resolve()

# Add backend directory to Python path if not already there
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

print(f"Backend directory: {backend_dir}")
print(f"Python path: {sys.path[:3]}")
print(f"Current working directory: {os.getcwd()}")

# Verify app module can be imported
try:
    import app
    print(f"Successfully imported app from: {app.__file__}")
except ImportError as e:
    print(f"ERROR: Failed to import app: {e}")
    sys.exit(1)

# Now import and run uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
