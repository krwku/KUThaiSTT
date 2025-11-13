#!/usr/bin/env python3
"""
Setup script for Thai STT Auto-Tagger

Install with: pip install -e .
Or: python setup.py install
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="thai-stt-auto-tagger",
    version="1.0.0",
    author="Your Name",  # UPDATE THIS
    author_email="your.email@example.com",  # UPDATE THIS
    description="Automated tagging system for Thai Speech-to-Text datasets with audio analysis and transcription",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/thai-stt-auto-tagger",  # UPDATE THIS
    project_urls={
        "Bug Reports": "https://github.com/yourusername/thai-stt-auto-tagger/issues",  # UPDATE THIS
        "Source": "https://github.com/yourusername/thai-stt-auto-tagger",  # UPDATE THIS
        "Documentation": "https://github.com/yourusername/thai-stt-auto-tagger/tree/main/docs",  # UPDATE THIS
    },
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Thai",
    ],
    keywords="thai speech-to-text stt annotation audio nlp machine-learning whisper dataset",
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "pydub>=0.25.0",
        "openai-whisper>=20230314",
        "pythainlp>=4.0.0",
        "attacut>=1.0.6",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "gui": [
            "pygame>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "thai-stt-tagger=thai_stt_auto_tagger:main",
            "thai-stt-gui=annotation_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
    zip_safe=False,
)
