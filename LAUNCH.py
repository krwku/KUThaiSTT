#!/usr/bin/env python3
"""
Thai STT Auto-Tagger Launcher

Double-click this file to run the tagger with an interactive menu.
"""

import os
import sys
import subprocess
from pathlib import Path
import platform

# Colors for different platforms
if platform.system() == "Windows":
    # Windows color codes
    os.system('')  # Enable ANSI colors on Windows 10+
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
else:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header():
    """Print the application header"""
    clear_screen()
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}🎤 Thai Speech-to-Text Auto-Tagger{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")

def check_requirements():
    """Check if basic requirements are met"""
    errors = []
    warnings = []
    
    # Check if main script exists
    if not Path("thai_stt_auto_tagger.py").exists():
        errors.append("thai_stt_auto_tagger.py not found in current directory")
    
    # Check if data directory exists
    if not Path("data").exists():
        warnings.append("'data' directory not found - will be created when needed")
    
    # Check Python packages
    try:
        import numpy
        import librosa
    except ImportError as e:
        errors.append(f"Missing required package: {e.name}")
        errors.append("Run: pip install -r requirements.txt")
    
    return errors, warnings

def print_menu():
    """Display the main menu"""
    print(f"{BOLD}Main Menu:{RESET}\n")
    print(f"  {GREEN}1{RESET}) {BOLD}Process all files (FAST - no transcription){RESET}")
    print(f"     ⚡ Quick audio analysis only (~1 second per file)")
    print()
    print(f"  {GREEN}2{RESET}) {BOLD}Process all files (FULL - with transcription){RESET}")
    print(f"     🎯 Complete analysis with Thai transcription (~30-120s per file)")
    print()
    print(f"  {GREEN}3{RESET}) {BOLD}Process single file{RESET}")
    print(f"     📄 Process one specific audio file")
    print()
    print(f"  {GREEN}4{RESET}) {BOLD}View quality statistics{RESET}")
    print(f"     📊 Show summary of processed files")
    print()
    print(f"  {GREEN}5{RESET}) {BOLD}Export to CSV{RESET}")
    print(f"     💾 Export metadata to spreadsheet format")
    print()
    print(f"  {GREEN}6{RESET}) {BOLD}Test installation{RESET}")
    print(f"     🔧 Check if all dependencies are installed")
    print()
    print(f"  {GREEN}7{RESET}) {BOLD}Help & Documentation{RESET}")
    print(f"     📖 View usage instructions")
    print()
    print(f"  {RED}0{RESET}) {BOLD}Exit{RESET}")
    print()

def run_command(cmd):
    """Run a command and handle errors"""
    try:
        if platform.system() == "Windows":
            # Use shell=True on Windows to find python
            result = subprocess.run(cmd, shell=True, check=True)
        else:
            result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}Error: Command failed with exit code {e.returncode}{RESET}")
        return False
    except FileNotFoundError:
        print(f"\n{RED}Error: Command not found. Make sure Python is installed.{RESET}")
        return False

def process_all_fast():
    """Process all files without transcription"""
    print_header()
    print(f"{BOLD}Processing All Files - FAST MODE{RESET}\n")
    
    if not Path("data").exists():
        print(f"{YELLOW}Creating 'data' directory...{RESET}")
        Path("data").mkdir()
        print(f"{RED}Please add MP3 files to the 'data' directory and try again.{RESET}")
        input("\nPress Enter to continue...")
        return
    
    mp3_files = list(Path("data").glob("*.mp3"))
    if not mp3_files:
        print(f"{RED}No MP3 files found in 'data' directory.{RESET}")
        print(f"Please add some audio files and try again.")
        input("\nPress Enter to continue...")
        return
    
    print(f"Found {GREEN}{len(mp3_files)}{RESET} MP3 files")
    print(f"Estimated time: ~{len(mp3_files)} seconds\n")
    
    proceed = input("Proceed? (Y/n): ").strip().lower()
    if proceed and proceed != 'y':
        return
    
    print()
    cmd = [sys.executable, "thai_stt_auto_tagger.py", "--input", "data/", "--all", "--no-transcription"]
    success = run_command(cmd)
    
    if success:
        print(f"\n{GREEN}✓ Processing complete!{RESET}")
        print(f"Check the 'metadata' directory for results.")
    
    input("\nPress Enter to continue...")

def process_all_full():
    """Process all files with transcription"""
    print_header()
    print(f"{BOLD}Processing All Files - FULL MODE{RESET}\n")
    
    if not Path("data").exists():
        print(f"{YELLOW}Creating 'data' directory...{RESET}")
        Path("data").mkdir()
        print(f"{RED}Please add MP3 files to the 'data' directory and try again.{RESET}")
        input("\nPress Enter to continue...")
        return
    
    mp3_files = list(Path("data").glob("*.mp3"))
    if not mp3_files:
        print(f"{RED}No MP3 files found in 'data' directory.{RESET}")
        print(f"Please add some audio files and try again.")
        input("\nPress Enter to continue...")
        return
    
    print(f"Found {GREEN}{len(mp3_files)}{RESET} MP3 files")
    print(f"Estimated time: ~{len(mp3_files) * 60 // 60} minutes (with transcription)\n")
    
    print(f"{BOLD}Select Whisper model:{RESET}")
    print(f"  1) tiny   - Fastest, least accurate")
    print(f"  2) base   - Fast, low accuracy")
    print(f"  3) small  - Balanced")
    print(f"  4) medium - Recommended (default)")
    print(f"  5) large  - Slowest, most accurate")
    
    choice = input("\nChoice [4]: ").strip() or "4"
    
    models = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large"}
    model = models.get(choice, "medium")
    
    print(f"\nUsing model: {GREEN}{model}{RESET}")
    print(f"{YELLOW}Note: First run will download the model (~244MB-1.5GB){RESET}\n")
    
    proceed = input("Proceed? (Y/n): ").strip().lower()
    if proceed and proceed != 'y':
        return
    
    print()
    cmd = [sys.executable, "thai_stt_auto_tagger.py", "--input", "data/", "--all", 
           "--whisper-model", model]
    success = run_command(cmd)
    
    if success:
        print(f"\n{GREEN}✓ Processing complete!{RESET}")
        print(f"Check the 'metadata' directory for results.")
    
    input("\nPress Enter to continue...")

def process_single():
    """Process a single file"""
    print_header()
    print(f"{BOLD}Process Single File{RESET}\n")
    
    if not Path("data").exists():
        print(f"{YELLOW}Creating 'data' directory...{RESET}")
        Path("data").mkdir()
        print(f"{RED}Please add MP3 files to the 'data' directory and try again.{RESET}")
        input("\nPress Enter to continue...")
        return
    
    mp3_files = list(Path("data").glob("*.mp3"))
    if not mp3_files:
        print(f"{RED}No MP3 files found in 'data' directory.{RESET}")
        input("\nPress Enter to continue...")
        return
    
    print(f"{BOLD}Available files:{RESET}\n")
    for i, f in enumerate(mp3_files, 1):
        print(f"  {i}) {f.name}")
    
    print()
    choice = input("Select file number: ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(mp3_files):
            raise ValueError()
        selected_file = mp3_files[idx]
    except (ValueError, IndexError):
        print(f"{RED}Invalid selection{RESET}")
        input("\nPress Enter to continue...")
        return
    
    transcribe = input("\nEnable transcription? (y/N): ").strip().lower()
    
    print()
    cmd = [sys.executable, "thai_stt_auto_tagger.py", "--input", "data/", 
           "--file", selected_file.name]
    
    if transcribe != 'y':
        cmd.append("--no-transcription")
    
    success = run_command(cmd)
    
    if success:
        print(f"\n{GREEN}✓ Processing complete!{RESET}")
    
    input("\nPress Enter to continue...")

def view_statistics():
    """View quality statistics"""
    print_header()
    print(f"{BOLD}Quality Statistics{RESET}\n")
    
    if not Path("metadata").exists() or not list(Path("metadata").glob("*_metadata.json")):
        print(f"{RED}No metadata files found.{RESET}")
        print(f"Please process some audio files first.")
        input("\nPress Enter to continue...")
        return
    
    # Quick stats using Python
    import json
    from collections import Counter
    
    metadata_files = list(Path("metadata").glob("*_metadata.json"))
    
    noise_levels = []
    clarity_levels = []
    snr_values = []
    durations = []
    
    for mf in metadata_files:
        with open(mf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        noise_levels.append(data['automated_tags']['noise_level'])
        clarity_levels.append(data['automated_tags']['speech_clarity'])
        snr_values.append(data['automated_tags']['snr_db'])
        durations.append(data['audio_properties']['duration_seconds'])
    
    print(f"{BOLD}Total files processed:{RESET} {GREEN}{len(metadata_files)}{RESET}")
    print(f"{BOLD}Total duration:{RESET} {sum(durations)/60:.1f} minutes\n")
    
    print(f"{BOLD}Noise Levels:{RESET}")
    for level, count in Counter(noise_levels).most_common():
        pct = count/len(metadata_files)*100
        print(f"  {level:20} {count:3} ({pct:5.1f}%)")
    
    print(f"\n{BOLD}Speech Clarity:{RESET}")
    for level, count in Counter(clarity_levels).most_common():
        pct = count/len(metadata_files)*100
        print(f"  {level:20} {count:3} ({pct:5.1f}%)")
    
    print(f"\n{BOLD}SNR Statistics:{RESET}")
    print(f"  Average: {sum(snr_values)/len(snr_values):.2f} dB")
    print(f"  Min:     {min(snr_values):.2f} dB")
    print(f"  Max:     {max(snr_values):.2f} dB")
    
    high_quality = sum(1 for i in range(len(metadata_files))
                      if snr_values[i] > 25 and clarity_levels[i] == 'clear_speech')
    print(f"\n{BOLD}High Quality Files:{RESET} {high_quality} ({high_quality/len(metadata_files)*100:.1f}%)")
    print(f"  (SNR > 25 dB and clear speech)")
    
    input("\n\nPress Enter to continue...")

def export_csv():
    """Export metadata to CSV"""
    print_header()
    print(f"{BOLD}Export to CSV{RESET}\n")
    
    if not Path("metadata").exists() or not list(Path("metadata").glob("*_metadata.json")):
        print(f"{RED}No metadata files found.{RESET}")
        print(f"Please process some audio files first.")
        input("\nPress Enter to continue...")
        return
    
    import json
    import csv
    
    metadata_files = list(Path("metadata").glob("*_metadata.json"))
    csv_path = Path("metadata") / "summary.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'Filename', 'Duration (s)', 'SNR (dB)', 'Noise Level',
            'Speech Clarity', 'Voice Activity (%)', 'Speaking Style',
            'Code Switching', 'Vocabulary Type', 'Transcription Available'
        ])
        
        for mf in metadata_files:
            with open(mf, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
            
            writer.writerow([
                data['file_info']['filename'],
                f"{data['audio_properties']['duration_seconds']:.2f}",
                f"{data['automated_tags']['snr_db']:.2f}",
                data['automated_tags']['noise_level'],
                data['automated_tags']['speech_clarity'],
                f"{data['automated_tags']['voice_activity_percentage']:.1f}",
                data['automated_tags']['speaking_style_suggested'],
                data['linguistic_analysis']['code_switching'],
                data['linguistic_analysis']['vocabulary_type_suggested'],
                'Yes' if data['transcription']['available'] else 'No'
            ])
    
    print(f"{GREEN}✓ CSV exported successfully!{RESET}")
    print(f"Location: {csv_path}")
    print(f"Exported {len(metadata_files)} files")
    
    input("\n\nPress Enter to continue...")

def test_installation():
    """Test if all dependencies are installed"""
    print_header()
    print(f"{BOLD}Testing Installation{RESET}\n")
    
    cmd = [sys.executable, "test_installation.py"]
    run_command(cmd)
    
    input("\n\nPress Enter to continue...")

def show_help():
    """Show help and documentation"""
    print_header()
    print(f"{BOLD}Help & Documentation{RESET}\n")
    
    print(f"{CYAN}Quick Start:{RESET}")
    print(f"  1. Place your MP3 files in the 'data' directory")
    print(f"  2. Choose option 1 for quick analysis (no transcription)")
    print(f"  3. Or choose option 2 for full analysis (with transcription)")
    print(f"  4. Results are saved in the 'metadata' directory\n")
    
    print(f"{CYAN}Processing Modes:{RESET}")
    print(f"  Fast Mode:  Audio analysis only (~1 second per file)")
    print(f"              - Noise level, clarity, voice activity")
    print(f"  Full Mode:  Includes transcription (~30-120s per file)")
    print(f"              - Everything in fast mode PLUS")
    print(f"              - Thai transcription, code-switching, vocabulary\n")
    
    print(f"{CYAN}Output:{RESET}")
    print(f"  Each file gets a JSON metadata file with:")
    print(f"  - Automated tags (noise, clarity, etc.)")
    print(f"  - Transcription (if enabled)")
    print(f"  - Linguistic analysis")
    print(f"  - Flags for manual review\n")
    
    print(f"{CYAN}Documentation Files:{RESET}")
    if Path("QUICKSTART.md").exists():
        print(f"  ✓ QUICKSTART.md   - 5-minute quick start guide")
    if Path("README.md").exists():
        print(f"  ✓ README.md       - Complete documentation")
    if Path("PROJECT_SUMMARY.md").exists():
        print(f"  ✓ PROJECT_SUMMARY.md - Project overview")
    
    print(f"\n{CYAN}System Info:{RESET}")
    print(f"  Python:   {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Current:  {Path.cwd()}")
    
    input("\n\nPress Enter to continue...")

def main():
    """Main application loop"""
    # Check requirements
    errors, warnings = check_requirements()
    
    if errors:
        print_header()
        print(f"{RED}{BOLD}⚠️  INSTALLATION ERRORS{RESET}\n")
        for error in errors:
            print(f"{RED}✗ {error}{RESET}")
        print(f"\n{YELLOW}Please fix these errors and run again.{RESET}")
        print(f"For help, see QUICKSTART.md or README.md")
        input("\nPress Enter to exit...")
        return
    
    if warnings:
        print_header()
        print(f"{YELLOW}{BOLD}⚠️  WARNINGS{RESET}\n")
        for warning in warnings:
            print(f"{YELLOW}! {warning}{RESET}")
        print()
        input("Press Enter to continue...")
    
    # Main menu loop
    while True:
        print_header()
        
        # Show data directory status
        if Path("data").exists():
            mp3_count = len(list(Path("data").glob("*.mp3")))
            if mp3_count > 0:
                print(f"{GREEN}📁 Data directory: {mp3_count} MP3 files ready{RESET}\n")
            else:
                print(f"{YELLOW}📁 Data directory: Empty (add MP3 files){RESET}\n")
        else:
            print(f"{RED}📁 Data directory: Not found (will be created){RESET}\n")
        
        print_menu()
        
        choice = input(f"{BOLD}Select option:{RESET} ").strip()
        
        if choice == '1':
            process_all_fast()
        elif choice == '2':
            process_all_full()
        elif choice == '3':
            process_single()
        elif choice == '4':
            view_statistics()
        elif choice == '5':
            export_csv()
        elif choice == '6':
            test_installation()
        elif choice == '7':
            show_help()
        elif choice == '0':
            print(f"\n{CYAN}Thanks for using Thai STT Auto-Tagger! Goodbye! 👋{RESET}\n")
            break
        else:
            print(f"\n{RED}Invalid option. Please try again.{RESET}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interrupted by user. Goodbye!{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
