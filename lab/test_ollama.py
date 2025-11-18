#!/usr/bin/env python3
"""
Quick test to verify Ollama connectivity
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import ollama
    
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    print(f"Testing Ollama connection...")
    print(f"  URL: {ollama_base_url}")
    print(f"  Model: {ollama_model}")
    
    # Simple test query
    response = ollama.chat(
        model=ollama_model,
        messages=[{"role": "user", "content": "Say 'OK' if you can hear me."}]
    )
    
    print(f"\n✓ Ollama is working!")
    print(f"  Response: {response['message']['content']}")
    print("\nYou can now run the simulation:")
    print("  python lab/run_simulation.py")
    
except ImportError:
    print("✗ Ollama package not installed")
    print("  Install with: pip install ollama")
    sys.exit(1)
except Exception as e:
    print(f"✗ Ollama connection failed: {e}")
    print("\nMake sure:")
    print("  1. Ollama is installed (https://ollama.ai)")
    print("  2. Ollama service is running: ollama serve")
    print("  3. Model is pulled: ollama pull llama3.2")
    print("\nNote: Simulation will use fallback mode if Ollama is unavailable")
    sys.exit(1)

