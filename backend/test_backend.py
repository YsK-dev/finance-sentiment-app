#!/usr/bin/env python3
"""
Quick test to verify backend can start
"""
import sys
import os

# Add the backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("🧪 Testing Backend Setup...")
print(f"Python: {sys.version}")
print(f"Backend dir: {backend_dir}")
print()

# Test 1: Import main modules
print("1️⃣ Testing imports...")
try:
    import uvicorn
    print("   ✅ uvicorn")
except ImportError as e:
    print(f"   ❌ uvicorn: {e}")
    sys.exit(1)

try:
    import fastapi
    print("   ✅ fastapi")
except ImportError as e:
    print(f"   ❌ fastapi: {e}")
    sys.exit(1)

try:
    import transformers
    print("   ✅ transformers (FinBERT)")
except ImportError as e:
    print(f"   ❌ transformers: {e}")
    sys.exit(1)

try:
    import torch
    print("   ✅ torch (PyTorch)")
except ImportError as e:
    print(f"   ❌ torch: {e}")
    sys.exit(1)

# Test 2: Import app modules
print()
print("2️⃣ Testing app modules...")
try:
    from app.main import app
    print("   ✅ app.main")
except Exception as e:
    print(f"   ❌ app.main: {e}")
    sys.exit(1)

try:
    from app.services.data_collector import DataCollector
    print("   ✅ DataCollector")
except Exception as e:
    print(f"   ❌ DataCollector: {e}")
    sys.exit(1)

try:
    from app.services.sentiment_analyzer import SentimentAnalyzer
    print("   ✅ SentimentAnalyzer")
except Exception as e:
    print(f"   ❌ SentimentAnalyzer: {e}")
    sys.exit(1)

# Test 3: Check .env file
print()
print("3️⃣ Checking configuration...")
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    print(f"   ✅ .env file exists")
    with open(env_path) as f:
        content = f.read()
        if 'NEWS_API_KEY' in content and len(content.split('NEWS_API_KEY=')[1].split()[0]) > 10:
            print("   ✅ NewsAPI key configured")
        if 'FINNHUB_API_KEY' in content and len(content.split('FINNHUB_API_KEY=')[1].split()[0]) > 10:
            print("   ✅ Finnhub key configured")
else:
    print(f"   ⚠️  .env file not found (optional)")

print()
print("╔════════════════════════════════════════════════════════════════╗")
print("║  ✅ ALL TESTS PASSED - Backend is ready to start!             ║")
print("╚════════════════════════════════════════════════════════════════╝")
print()
print("🚀 To start the backend:")
print("   cd backend")
print("   source .venv/bin/activate")
print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print()
