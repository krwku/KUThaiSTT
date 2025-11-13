#!/bin/bash
# Thai STT Auto-Tagger Launcher for Mac/Linux
# Make executable with: chmod +x LAUNCH.sh
# Then double-click or run: ./LAUNCH.sh

echo "========================================================================"
echo "🎤 Thai Speech-to-Text Auto-Tagger"
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.8 or later:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"
echo ""

# Check if required files exist
if [ ! -f "LAUNCH.py" ]; then
    echo "❌ ERROR: LAUNCH.py not found in current directory"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the launcher
python3 LAUNCH.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ An error occurred."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
