#!/usr/bin/env python
"""
Novel Translator - Başlatma Scripti
Bu script uygulamayı başlatır ve gerekli kontrolları yapar.
"""

import sys
import subprocess
import os

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_dependencies():
    """Check required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages found:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 To install: pip install -r requirements.txt")
        
        response = input("\nInstall now? (y/n): ")
        if response.lower() in ['e', 'evet', 'y', 'yes']:
            print("\n📦 Installing packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Packages installed successfully!")
        else:
            sys.exit(1)
    else:
        print("✅ All required packages installed")

def create_env_file():
    """Create .env file if not exists"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📝 Creating .env file...")
            with open('.env.example', 'r', encoding='utf-8') as f:
                content = f.read()
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ .env file created")
    else:
        print("✅ .env file exists")

def create_static_folder():
    """Check static folder"""
    if not os.path.exists('static'):
        print("📁 Creating static folder...")
        os.makedirs('static')
        print("✅ Static folder created")
    else:
        print("✅ Static folder exists")

def start_server():
    """Start Uvicorn server"""
    print("\n" + "="*50)
    print("🚀 Starting Novel Translator...")
    print("="*50)
    print("\n📍 URL: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("\n⌨️  To stop: Press Ctrl+C\n")
    print("="*50 + "\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Novel Translator stopped. See you!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("\n" + "="*50)
    print("📚 Novel Translator - Setup Checks")
    print("="*50 + "\n")
    
    # Run checks
    check_python_version()
    check_dependencies()
    create_env_file()
    create_static_folder()
    
    print("\n✅ All checks completed!\n")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()

