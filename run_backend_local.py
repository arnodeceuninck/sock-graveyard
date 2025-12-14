#!/usr/bin/env python3
"""
Run the FastAPI backend locally without Docker

This script runs the backend server with hot-reload enabled for development.
No PostgreSQL or Redis required - uses SQLite by default.

Usage:
    python run_backend_local.py [--port 8000] [--host 0.0.0.0]
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Add backend to path
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))


def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    try:
        import sqlalchemy
    except ImportError:
        missing.append("sqlalchemy")
    
    try:
        import jwt
    except ImportError:
        missing.append("pyjwt")
    
    if missing:
        print("[ERROR] Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall them with:")
        print(f"   .venv\\Scripts\\pip install {' '.join(missing)}")
        print("\nOr run the setup script:")
        print("   .\\setup_local_dev.ps1")
        return False
    
    return True


def setup_environment():
    """Setup environment variables and directories"""
    
    # Check for .env file
    env_file = project_root / ".env"
    env_local_file = project_root / ".env.local"
    
    if not env_file.exists():
        if env_local_file.exists():
            print(f"ℹ️  No .env file found, using .env.local as template")
            print(f"ℹ️  Consider copying .env.local to .env for local development")
            # Load from .env.local
            os.environ.setdefault("ENV_FILE", str(env_local_file))
        else:
            print("⚠️  No .env file found. Using default configuration.")
            # Set default values
            os.environ.setdefault("DATABASE_URL", "sqlite:///./sock_graveyard_local.db")
            os.environ.setdefault("SECRET_KEY", "local-dev-secret-key-change-in-production")
            os.environ.setdefault("ENVIRONMENT", "development")
            os.environ.setdefault("UPLOAD_DIR", "images_local")
    
    # Create necessary directories
    upload_dir = os.environ.get("UPLOAD_DIR", "images_local")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print(f"✅ Upload directory: {upload_dir}")
    print(f"✅ Database: {os.environ.get('DATABASE_URL', 'sqlite:///./sock_graveyard_local.db')}")


def main():
    parser = argparse.ArgumentParser(description="Run Sock Graveyard backend locally")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload (default: True)")
    parser.add_argument("--no-reload", action="store_false", dest="reload", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🧦 SOCK GRAVEYARD - LOCAL BACKEND SERVER")
    print("=" * 80)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    print()
    print(f"🚀 Starting backend server on http://{args.host}:{args.port}")
    print(f"📚 API docs available at http://{args.host}:{args.port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if args.reload else 'disabled'}")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    # Run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            reload_dirs=[str(backend_path / "app")] if args.reload else None,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
