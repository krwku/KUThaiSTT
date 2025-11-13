#!/bin/bash
# Annotation GUI Launcher for Mac/Linux
# Make executable with: chmod +x LAUNCH_GUI.sh
# Then double-click or run: ./LAUNCH_GUI.sh

echo "========================================"
echo "Thai STT Annotation GUI"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.8+ from:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if metadata directory exists
if [ ! -d "metadata" ]; then
    echo "⚠️  WARNING: 'metadata' directory not found"
    echo ""
    echo "Please process audio files first to generate metadata."
    echo "Run: ./LAUNCH.sh and select option 1 or 2"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for pygame (optional)
if ! python3 -c "import pygame" 2>/dev/null; then
    echo ""
    echo "ℹ️  NOTE: pygame not installed - audio playback will be disabled"
    echo "To enable audio playback, run:"
    echo "    pip3 install pygame"
    echo ""
    echo "Continuing without audio playback..."
    sleep 3
fi

echo "Starting Annotation GUI..."
echo ""

# Run the GUI
python3 annotation_gui.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ An error occurred while running the GUI."
    echo ""
    echo "Common solutions:"
    echo "  1. Make sure annotation_gui.py is in the current directory"
    echo "  2. Install required packages: pip3 install -r requirements.txt"
    echo "  3. Check the error message above for details"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
