# 📦 Installation Guide - Novel Translator v2.0

## Quick Install (Recommended)

### For Windows

1. **Download** the project
   - Download ZIP from GitHub
   - Extract to your desired location

2. **Double-click** `start.bat`
   - That's it! Will automatically:
     - Check Python version
     - Install packages
     - Start server
     - Open browser

### For Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Novel-Translator.git
cd Novel-Translator

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run
python3 run.py
```

---

## Detailed Installation

### Prerequisites

#### Required:
- **Python** 3.8+ (3.11 recommended)
  - Download: https://www.python.org/downloads/
  - Make sure "Add Python to PATH" is checked during installation
- **pip** (comes with Python)

#### Recommended:
- **Git** for easy updates
- **Virtual environment** for clean installation

### Step-by-Step Guide

#### Step 1: Get the Code

**Option A: Git Clone (Recommended)**
```bash
git clone https://github.com/yourusername/Novel-Translator.git
cd Novel-Translator
```

**Option B: Download ZIP**
1. Click "Code" → "Download ZIP" on GitHub
2. Extract to folder
3. Open terminal/command prompt in that folder

#### Step 2: Create Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install ~33 packages (~100MB):
- FastAPI & Uvicorn (web server)
- SQLAlchemy (database)
- AI Provider SDKs (OpenAI, Gemini, DeepL, etc.)
- Export libraries (PDF, EPUB, DOCX)
- Utilities (pandas, tiktoken, etc.)

**Time**: 2-5 minutes depending on internet speed

#### Step 4: Run the Application

```bash
python run.py
```

You should see:
```
==================================================
📚 Novel Translator - Setup Checks
==================================================

✅ Python version: 3.11.x
✅ All required packages installed
✅ .env file exists
✅ Static folder exists

✅ All checks completed!

==================================================
🚀 Starting Novel Translator...
==================================================

📍 URL: http://localhost:8000
📍 API Docs: http://localhost:8000/docs

⌨️  To stop: Press Ctrl+C
==================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Step 5: Open in Browser

Navigate to: **http://localhost:8000**

You should see the Novel Translator interface! 🎉

---

## Verification

### Check Installation

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version

# Check if FastAPI is installed
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__}')"

# Check all imports
python -c "from main import app; print('✅ Application ready!')"
```

### Test Run

1. Open http://localhost:8000
2. Should see "Novel Translator" interface
3. Click "Settings" → "AI Provider Configuration"
4. Add an API key (Gemini is free!)
5. Create a test project
6. Add a test chapter
7. Translate!

---

## Troubleshooting

### "Python not found"
- Install Python from https://python.org
- Make sure "Add to PATH" was checked
- Restart terminal/command prompt

### "pip not found"
```bash
# Windows
python -m pip --version

# Linux/Mac
python3 -m pip --version
```

### "ModuleNotFoundError"
```bash
# Reinstall all packages
pip install -r requirements.txt --force-reinstall
```

### "Port 8000 already in use"
```bash
# Use different port
uvicorn main:app --port 8001
```

### "Permission denied" (Linux/Mac)
```bash
# Use sudo or install in user space
pip install -r requirements.txt --user
```

### Database Issues
```bash
# Delete and recreate database
rm novel_translator.db  # Linux/Mac
del novel_translator.db # Windows

# Restart app - will auto-create
python run.py
```

---

## Platform-Specific Notes

### Windows
- ✅ Use `python` command
- ✅ Double-click `start.bat` for easy start
- ✅ PowerShell or CMD both work
- ⚠️ May need to run as Administrator for first install

### Linux
- ✅ Use `python3` and `pip3`
- ✅ May need `python3-venv` package
- ✅ Install: `sudo apt install python3-venv` (Ubuntu/Debian)

### macOS
- ✅ Use `python3` and `pip3`
- ✅ May need Xcode Command Line Tools
- ✅ Install: `xcode-select --install`

---

## Update Instructions

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python run.py
```

---

## Uninstall

```bash
# Delete project folder
cd ..
rm -rf Novel-Translator  # Linux/Mac
rmdir /s Novel-Translator  # Windows

# If using virtual environment, just delete the folder
# Database and user data will be removed
```

---

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/novel-translator.service`:
```ini
[Unit]
Description=Novel Translator
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Novel-Translator
ExecStart=/usr/bin/python3 /path/to/Novel-Translator/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable novel-translator
sudo systemctl start novel-translator
```

### Using Docker (Coming Soon)

```dockerfile
# Dockerfile will be added in future update
```

---

## Getting Help

- 📖 Read [`README.md`](README.md)
- 🚀 Check [`QUICKSTART.md`](QUICKSTART.md)
- 🐛 Open GitHub Issue
- 💬 Check existing issues first

---

**Installation Time**: ~5-10 minutes
**Difficulty**: Easy ⭐⭐☆☆☆

© 2025 Novel Translator Project

