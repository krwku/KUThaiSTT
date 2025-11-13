# Thai Speech-to-Text Auto-Tagger 🎤🇹🇭

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Automated tagging system for Thai Speech-to-Text datasets with audio analysis, transcription, and metadata generation.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Output Format](#output-format)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

---

## 🎯 Overview

This tool automates the annotation process for Thai speech-to-text datasets, reducing manual effort by **60-70%** while maintaining quality through strategic human-in-the-loop validation. It's designed for building high-quality STT benchmarks and training datasets.

**Key Benefits:**
- ⚡ **Fast Processing**: 1 second per file without transcription, ~30s with transcription (GPU)
- 🎯 **High Accuracy**: SNR-based noise classification, acoustic feature analysis
- 🤖 **Smart Automation**: Automated tagging with confidence scoring
- 🔍 **Human-in-the-Loop**: Flags uncertain predictions for manual review
- 🇹🇭 **Thai-Optimized**: Handles Thai language nuances, code-switching, text normalization

---

## ✨ Features

### Fully Automated Tags (High Reliability ✅)
- **Noise Level** (`low_noise`, `medium_noise`, `high_noise`) - SNR-based classification
- **Speech Clarity** (`clear_speech`, `muffled_speech`, `distorted_speech`) - Acoustic feature analysis
- **Voice Activity Detection** - Percentage of speech vs. silence
- **Code-Switching Detection** (`none`, `some`, `frequent`) - Thai-English mixing patterns

### Automated Suggestions (Require Review 🔍)
- **Speaking Style** - Suggests `read_speech`, `spontaneous_speech`, or `conversational`
- **Vocabulary Type** - Suggests `general`, `business`, `medical`, or `technical` vocabulary

### Optional Features
- **🎤 Automatic Transcription** - Uses OpenAI Whisper for Thai ASR
- **📝 Text Normalization** - Thai text normalization using PyThaiNLP
- **🔤 Linguistic Analysis** - Extracts features from transcriptions
- **🖥️ GUI Annotation Tool** - Review and correct automated tags

---

## 🚀 Quick Start

### 1️⃣ One-Command Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thai-stt-auto-tagger.git
cd thai-stt-auto-tagger

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (choose your OS)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

### 2️⃣ Run the Interactive Launcher

**Windows:**
```bash
# Double-click LAUNCH.bat
# OR from command line:
LAUNCH.bat
```

**Mac/Linux:**
```bash
# Make executable and run:
chmod +x LAUNCH.sh
./LAUNCH.sh
```

**All Platforms:**
```bash
python LAUNCH.py
```

### 3️⃣ Process Your Audio Files

1. Create a `data/` folder and add your MP3 files
2. Select option **1** (Fast mode without transcription) or **2** (Full mode with transcription)
3. Find results in `metadata/` folder

**📖 For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)**

---

## 💿 Installation

### Requirements

- **Python 3.8+**
- **FFmpeg** (for audio processing)
- **4GB RAM** minimum (8GB+ recommended for transcription)
- **GPU** (optional, for faster transcription)

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/thai-stt-auto-tagger.git
   cd thai-stt-auto-tagger
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add to system PATH

4. **(Optional) GPU Support for Faster Transcription:**
   ```bash
   # For CUDA 11.8
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

5. **Verify installation:**
   ```bash
   python LAUNCH.py
   # Select option 6: Test installation
   ```

---

## 📖 Usage

### Command Line Interface

#### Process All Files
```bash
python thai_stt_auto_tagger.py --input data/ --all
```

#### Process Single File
```bash
python thai_stt_auto_tagger.py --input data/ --file sample.mp3
```

#### Fast Mode (No Transcription)
```bash
python thai_stt_auto_tagger.py --input data/ --all --no-transcription
```

#### Custom Whisper Model
```bash
# Faster (less accurate)
python thai_stt_auto_tagger.py --input data/ --all --whisper-model small

# More accurate (slower)
python thai_stt_auto_tagger.py --input data/ --all --whisper-model large
```

### Interactive Launcher

The easiest way to use the tool:

```bash
# Windows
LAUNCH.bat

# Mac/Linux
./LAUNCH.sh

# Any platform
python LAUNCH.py
```

**Available Options:**
1. Process all files (FAST - no transcription)
2. Process all files (FULL - with transcription)
3. Process single file
4. View quality statistics
5. Export to CSV
6. Test installation
7. Help & Documentation

### GUI Annotation Tool

Review and correct automated tags with a graphical interface:

```bash
# Windows
LAUNCH_GUI.bat

# Mac/Linux
./LAUNCH_GUI.sh

# Any platform
python annotation_gui.py
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--input` | `-i` | Input directory containing audio files | Required |
| `--file` | `-f` | Process a single specific file | None |
| `--all` | `-a` | Process all files matching pattern | False |
| `--output` | `-o` | Output directory for metadata | `metadata/` |
| `--no-transcription` | | Skip transcription for faster processing | False |
| `--whisper-model` | | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) | `medium` |
| `--pattern` | | File pattern to match (e.g., `*.wav`) | `*.mp3` |

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Detailed running instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[docs/](docs/)** - Project documentation and research papers

### Research & Design Documents

This tool is based on comprehensive research into Thai STT benchmarking:

- **[Thai STT Whitepaper](docs/thai_stt_whitepaper.md)** - Complete benchmark framework
- **[Tagging System Design](docs/tagging_system_design.md)** - Automation strategy
- **[Text Normalization Guidelines](docs/text_normalization.md)** - Thai text processing
- **[Annotator Instructions](docs/annotator_instructions.md)** - Human annotation guide

---

## 📊 Output Format

Metadata files are saved as JSON:

```json
{
  "file_info": {
    "filename": "sample.mp3",
    "processed_at": "2025-11-06T10:30:00",
    "file_size_bytes": 1234567
  },
  "audio_properties": {
    "duration_seconds": 15.5,
    "sample_rate": 16000
  },
  "automated_tags": {
    "noise_level": "low_noise",
    "snr_db": 28.5,
    "speech_clarity": "clear_speech",
    "speaking_style_suggested": "spontaneous_speech",
    "voice_activity_percentage": 85.3
  },
  "transcription": {
    "available": true,
    "text_raw": "สวัสดีครับ ผมชื่อสมชาย...",
    "text_normalized": "สวัสดีครับผมชื่อสมชาย...",
    "language_detected": "th"
  },
  "linguistic_analysis": {
    "code_switching": "some_code_switching",
    "vocabulary_type_suggested": "business_vocab"
  },
  "manual_review_required": {
    "speaker_gender": "required",
    "dialect": "required",
    "speaking_style_confirmation": "recommended"
  },
  "quality_flags": {
    "low_snr_warning": false,
    "short_duration_warning": false,
    "transcription_confidence": "high"
  }
}
```

---

## ⚡ Performance

### Processing Speed

| Mode | Speed (per file) | Best For |
|------|------------------|----------|
| **Fast Mode** (no transcription) | ~1 second | Initial tagging, large datasets |
| **Full Mode** (CPU) | ~30-120 seconds | Accurate transcription |
| **Full Mode** (GPU) | ~5-15 seconds | Fast & accurate |

### Automation Statistics

| Feature | Automation Level | Time Saved |
|---------|------------------|------------|
| Noise Level | 100% automated | ✅ Complete |
| Voice Activity | 100% automated | ✅ Complete |
| Speech Clarity | Automated + review | 🔄 ~70% |
| Code-Switching* | 100% automated | ✅ Complete |
| Speaking Style | Suggestion only | 🔄 ~40% |
| Vocabulary Type* | Suggestion only | 🔄 ~50% |

*Requires transcription to be enabled

**Overall time savings: ~60-70% of manual annotation effort**

### Whisper Model Comparison

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| `tiny` | 39M | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick testing |
| `base` | 74M | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast processing |
| `small` | 244M | ⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| **`medium`** | 769M | ⚡⚡ | ⭐⭐⭐⭐⭐ | **Default (recommended)** |
| `large` | 1550M | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy |

---

## 📁 Project Structure

```
thai-stt-auto-tagger/
├── 📄 thai_stt_auto_tagger.py    # Main tagging script
├── 🖥️ annotation_gui.py           # GUI for manual review
├── 🚀 LAUNCH.py                   # Interactive launcher
├── 🪟 LAUNCH.bat                  # Windows launcher
├── 🐧 LAUNCH.sh                   # Mac/Linux launcher
├── 🪟 LAUNCH_GUI.bat              # Windows GUI launcher
├── 🐧 LAUNCH_GUI.sh               # Mac/Linux GUI launcher
│
├── 📋 requirements.txt            # Python dependencies
├── ⚙️ config_template.json        # Configuration template
├── 📜 LICENSE                     # MIT License
│
├── 📖 README.md                   # This file
├── 📖 QUICKSTART.md               # 5-minute guide
├── 📖 HOW_TO_RUN.md               # Detailed instructions
├── 📖 CONTRIBUTING.md             # Contribution guide
│
├── 📁 docs/                       # Documentation
│   ├── thai_stt_whitepaper.md
│   ├── tagging_system_design.md
│   ├── text_normalization.md
│   └── annotator_instructions.md
│
├── 📁 data/                       # Input audio files (not in git)
│   └── *.mp3
│
├── 📁 metadata/                   # Output metadata (not in git)
│   └── *_metadata.json
│
└── 📁 examples/                   # Example scripts
    └── example_usage.py
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 **Report bugs** via GitHub Issues
- ✨ **Suggest features** or improvements
- 📝 **Improve documentation**
- 🔧 **Submit pull requests**
- 🌐 **Add language support** for other Thai dialects
- 📊 **Share your results** and use cases

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/thai-stt-auto-tagger.git
cd thai-stt-auto-tagger

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and test
python thai_stt_auto_tagger.py --input data/ --all

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📖 Citation

If you use this tool in your research, please cite:

```bibtex
@software{thai_stt_auto_tagger,
  title = {Thai Speech-to-Text Auto-Tagger},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/thai-stt-auto-tagger},
  note = {Automated annotation system for Thai STT datasets}
}
```

For the underlying research, please also cite the Thai STT Benchmark whitepaper:

```bibtex
@techreport{thai_stt_benchmark_2025,
  title = {Thai Speech-to-Text Benchmark Dataset: An Independent Evaluation Framework},
  author = {Your Team},
  year = {2025},
  institution = {Your Organization},
  type = {White Paper}
}
```

---

## 🙏 Acknowledgments

This project is based on:
- **OpenAI Whisper** for speech recognition
- **PyThaiNLP** for Thai text processing
- **librosa** for audio analysis
- Research in Thai language technology and STT benchmarking

### References

1. **PyThaiNLP**: Thai language processing library  
   [https://github.com/PyThaiNLP/pythainlp](https://github.com/PyThaiNLP/pythainlp)

2. **OpenAI Whisper**: Robust speech recognition  
   [https://github.com/openai/whisper](https://github.com/openai/whisper)

3. **Thai STT Research**: See [docs/thai_stt_whitepaper.md](docs/thai_stt_whitepaper.md) for full references

---

## 🆘 Support

### Getting Help

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/thai-stt-auto-tagger/issues)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/thai-stt-auto-tagger/discussions)
- 📧 Email: your-email@example.com

### Common Issues

See the [Troubleshooting](README.md#troubleshooting) section in the full README.

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/thai-stt-auto-tagger&type=Date)](https://star-history.com/#yourusername/thai-stt-auto-tagger&Date)

---

**Built with ❤️ for the Thai NLP community** 🇹🇭

---

## 📊 Project Status

- ✅ Core functionality implemented
- ✅ Audio analysis and tagging
- ✅ Whisper integration for transcription
- ✅ Text normalization
- ✅ GUI annotation tool
- 🔄 Additional Thai dialect support (planned)
- 🔄 Speaker diarization (planned)
- 🔄 Web interface (planned)

Last updated: November 2025
