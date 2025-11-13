#!/usr/bin/env python3
"""
Thai Speech-to-Text Dataset Auto-Tagger

This script automates the tagging process for Thai STT datasets by:
1. Analyzing audio files (MP3) for acoustic properties
2. Auto-transcribing speech using Whisper
3. Detecting code-switching and other linguistic features
4. Generating structured metadata files

Usage:
    python thai_stt_auto_tagger.py --input data/ --all
    python thai_stt_auto_tagger.py --input data/ --file sample.mp3
"""

import os
import json
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment

warnings.filterwarnings('ignore')

# Progress tracking utilities
def print_progress(message, level=0):
    """Print progress message with indentation"""
    indent = "  " * level
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {indent}{message}")

def time_operation(func):
    """Decorator to time operations"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        return result, elapsed
    return wrapper

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not installed. Transcription will be skipped.")
    print("Install with: pip install openai-whisper")

try:
    from pythainlp.util import normalize
    from pythainlp.tokenize import word_tokenize
    PYTHAINLP_AVAILABLE = True
except ImportError:
    PYTHAINLP_AVAILABLE = False
    print("Warning: pythainlp not installed. Thai text processing will be limited.")
    print("Install with: pip install pythainlp")


class AudioAnalyzer:
    """Analyzes audio files for acoustic properties"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and convert to mono"""
        import os
        
        # Check file exists and get info
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        print_progress(f"File size: {file_size_mb:.2f} MB", 1)
        
        # Try librosa first (recommended method)
        try:
            print_progress("Attempting to load with librosa...", 1)
            print_progress("(This may take 10-30 seconds for large files)", 2)
            
            # Use a shorter hop_length for faster loading
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            
            print_progress(f"✓ Loaded {len(y)/sr:.1f}s of audio", 2)
            print_progress(f"✓ Sample rate: {sr} Hz", 2)
            return y, sr
            
        except KeyboardInterrupt:
            print_progress("⚠ Loading interrupted by user", 1)
            raise
            
        except Exception as e:
            error_msg = str(e)
            print_progress(f"⚠ librosa failed: {error_msg[:80]}", 1)
            
            # Check if it's an FFmpeg-related error
            if 'ffmpeg' in error_msg.lower() or 'audioread' in error_msg.lower():
                print_progress("⚠ This appears to be an FFmpeg issue", 2)
                print_progress("  Install FFmpeg and try again", 2)
            
            # Fallback to pydub for MP3
            try:
                print_progress("Attempting to load with pydub (fallback)...", 1)
                print_progress("(This may take longer)", 2)
                
                audio = AudioSegment.from_mp3(file_path)
                print_progress("Converting to mono...", 2)
                audio = audio.set_channels(1)  # Convert to mono
                print_progress("Resampling to target rate...", 2)
                audio = audio.set_frame_rate(self.sample_rate)
                print_progress("Converting to numpy array...", 2)
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                samples = samples / (2**15)  # Normalize to [-1, 1]
                
                print_progress(f"✓ Loaded {len(samples)/self.sample_rate:.1f}s of audio", 2)
                return samples, self.sample_rate
                
            except KeyboardInterrupt:
                print_progress("⚠ Loading interrupted by user", 1)
                raise
                
            except Exception as e2:
                error_msg2 = str(e2)
                print_progress(f"❌ pydub also failed: {error_msg2[:80]}", 1)
                print()
                print(f"{'='*70}")
                print(f"ERROR: Could not load audio file")
                print(f"{'='*70}")
                print(f"File: {file_path}")
                print(f"Size: {file_size_mb:.2f} MB")
                print()
                print("Error details:")
                print(f"  librosa: {error_msg}")
                print(f"  pydub:   {error_msg2}")
                print()
                print("Possible causes:")
                print("  • FFmpeg is not installed or not in PATH")
                print("  • Audio file is corrupted or in unsupported format")
                print("  • File path contains special characters")
                print("  • Insufficient memory for large file")
                print()
                print("Solutions:")
                print("  1. Install FFmpeg:")
                print("     Windows: Download from https://ffmpeg.org/")
                print("     Ubuntu: sudo apt-get install ffmpeg")
                print("     macOS: brew install ffmpeg")
                print()
                print("  2. Convert the file to standard format:")
                print(f"     ffmpeg -i \"{file_path}\" -ar 16000 -ac 1 output.mp3")
                print()
                print("  3. Check if file is corrupted:")
                print(f"     Try playing it in a media player")
                print(f"{'='*70}")
                raise RuntimeError(f"Failed to load audio file: {file_path}")
    
    def calculate_snr(self, y: np.ndarray, frame_length: int = 2048, 
                      hop_length: int = 512) -> float:
        """
        Calculate Signal-to-Noise Ratio (SNR) in dB
        Uses energy-based approach to estimate signal vs noise
        """
        # Calculate RMS energy per frame
        rms = librosa.feature.rms(y=y, frame_length=frame_length, 
                                  hop_length=hop_length)[0]
        
        # Separate signal and noise using percentile threshold
        threshold = np.percentile(rms, 20)  # Bottom 20% considered noise
        
        noise_frames = rms[rms < threshold]
        signal_frames = rms[rms >= threshold]
        
        if len(noise_frames) == 0 or len(signal_frames) == 0:
            return 30.0  # Default high SNR if can't separate
        
        signal_power = np.mean(signal_frames ** 2)
        noise_power = np.mean(noise_frames ** 2)
        
        if noise_power == 0:
            return 40.0  # Very clean signal
        
        snr_db = 10 * np.log10(signal_power / noise_power)
        return float(snr_db)
    
    def classify_noise_level(self, snr_db: float) -> str:
        """
        Classify noise level based on SNR
        Thresholds based on typical audio quality standards
        """
        if snr_db > 25:
            return "low_noise"
        elif snr_db > 15:
            return "medium_noise"
        else:
            return "high_noise"
    
    def analyze_speech_clarity(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze speech clarity using multiple acoustic features
        """
        # Extract features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
        
        # MFCC statistics (useful for clarity)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.mean(np.std(mfccs, axis=1))
        
        # Spectral flatness (indicates noisiness)
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
        
        return {
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zero_crossing_rate),
            'mfcc_std': float(mfcc_std),
            'spectral_flatness': float(spectral_flatness)
        }
    
    def classify_speech_clarity(self, clarity_features: Dict[str, float], 
                                snr_db: float) -> str:
        """
        Classify speech clarity based on acoustic features
        This is a heuristic approach - can be improved with ML model
        """
        # High spectral flatness indicates noise/distortion
        if clarity_features['spectral_flatness'] > 0.5 or snr_db < 10:
            return "distorted_speech"
        
        # Low SNR or high variability indicates muffled speech
        if snr_db < 20 and clarity_features['mfcc_std'] < 10:
            return "muffled_speech"
        
        return "clear_speech"
    
    def detect_voice_activity(self, y: np.ndarray, sr: int, 
                              top_db: int = 30) -> float:
        """
        Detect percentage of speech activity in audio
        """
        # Use librosa's built-in voice activity detection
        intervals = librosa.effects.split(y, top_db=top_db)
        
        if len(intervals) == 0:
            return 0.0
        
        speech_duration = sum([end - start for start, end in intervals])
        total_duration = len(y)
        
        speech_percentage = (speech_duration / total_duration) * 100
        return float(speech_percentage)
    
    def analyze_speaking_style(self, y: np.ndarray, sr: int) -> Dict[str, any]:
        """
        Analyze speaking style characteristics
        Helps distinguish between read, spontaneous, and conversational speech
        """
        # Detect pauses
        intervals = librosa.effects.split(y, top_db=30)
        
        if len(intervals) < 2:
            pause_count = 0
            avg_pause_duration = 0
        else:
            pauses = []
            for i in range(len(intervals) - 1):
                pause_start = intervals[i][1]
                pause_end = intervals[i + 1][0]
                pause_duration = (pause_end - pause_start) / sr
                if pause_duration > 0.1:  # Minimum 100ms to count as pause
                    pauses.append(pause_duration)
            
            pause_count = len(pauses)
            avg_pause_duration = np.mean(pauses) if pauses else 0
        
        # Speaking rate (syllables per second estimate)
        speech_segments = [y[start:end] for start, end in intervals]
        total_speech_duration = sum([len(seg) / sr for seg in speech_segments])
        
        # Estimate energy variations (more variation = less monotonous)
        rms = librosa.feature.rms(y=y)[0]
        energy_variation = float(np.std(rms))
        
        return {
            'pause_count': pause_count,
            'avg_pause_duration': float(avg_pause_duration),
            'speech_percentage': self.detect_voice_activity(y, sr),
            'energy_variation': energy_variation,
            'total_duration': float(len(y) / sr)
        }
    
    def classify_speaking_style(self, style_features: Dict[str, any]) -> str:
        """
        Classify speaking style based on acoustic features
        Note: This is a basic heuristic approach
        """
        pause_rate = style_features['pause_count'] / (style_features['total_duration'] / 60)
        
        # Read speech: few pauses, consistent energy
        if (pause_rate < 5 and 
            style_features['energy_variation'] < 0.05 and
            style_features['avg_pause_duration'] < 0.5):
            return "read_speech"
        
        # Spontaneous speech: more pauses, variable energy
        if pause_rate > 5 and style_features['avg_pause_duration'] > 0.3:
            return "spontaneous_speech"
        
        # Default to spontaneous for ambiguous cases
        return "spontaneous_speech"


class SpeechTranscriber:
    """Handles speech transcription using Whisper"""
    
    def __init__(self, model_name: str = "medium"):
        if not WHISPER_AVAILABLE:
            self.model = None
            return
        
        print(f"Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        print("Model loaded successfully!")
    
    def transcribe(self, audio_path: str) -> Optional[Dict[str, any]]:
        """Transcribe audio file to text"""
        if not WHISPER_AVAILABLE or self.model is None:
            return None
        
        try:
            result = self.model.transcribe(
                audio_path,
                language="th",  # Thai language
                task="transcribe",
                fp16=False  # Set to True if using GPU
            )
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'th'),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            print(f"Transcription error: {e}")
            return None


class LanguageAnalyzer:
    """Analyzes transcribed text for linguistic features"""
    
    def __init__(self):
        self.thai_available = PYTHAINLP_AVAILABLE
    
    def detect_code_switching(self, text: str) -> str:
        """
        Detect code-switching (binary: yes or no)
        Returns 'code_switching' if ANY non-Thai words detected, otherwise 'no_code_switching'
        """
        if not text:
            return "no_code_switching"
        
        # Count Thai characters vs Latin characters
        thai_chars = sum(1 for c in text if '\u0E00' <= c <= '\u0E7F')
        latin_chars = sum(1 for c in text if ('a' <= c.lower() <= 'z'))
        total_alpha = thai_chars + latin_chars
        
        if total_alpha == 0:
            return "no_code_switching"
        
        # Calculate percentage of non-Thai characters
        non_thai_percentage = (latin_chars / total_alpha) * 100
        
        # Binary classification: ANY non-Thai content = code-switching
        if non_thai_percentage < 5:  # Less than 5% = noise/threshold
            return "no_code_switching"
        else:
            return "code_switching"
    
    def analyze_vocabulary_type(self, text: str) -> str:
        """
        Analyze vocabulary type based on keywords
        This is a basic implementation - can be enhanced with domain-specific lexicons
        """
        if not text:
            return "general_vocab"
        
        text_lower = text.lower()
        
        # Define domain-specific keywords (partial lists for demonstration)
        business_keywords = [
            'roi', 'stakeholder', 'revenue', 'profit', 'ผลกำไร', 'รายได้',
            'ธุรกิจ', 'การตลาด', 'ลงทุน', 'หุ้น', 'บริษัท', 'กำไร'
        ]
        
        medical_keywords = [
            'patient', 'doctor', 'hospital', 'ผู้ป่วย', 'แพทย์', 'โรงพยาบาล',
            'อาการ', 'การรักษา', 'โรค', 'ยา', 'การวินิจฉัย', 'myocardial'
        ]
        
        technical_keywords = [
            'database', 'server', 'code', 'algorithm', 'deploy', 'api',
            'โปรแกรม', 'ระบบ', 'เซิร์ฟเวอร์', 'คอมพิวเตอร์', 'software', 'hardware'
        ]
        
        # Count domain-specific keywords
        business_count = sum(1 for kw in business_keywords if kw in text_lower)
        medical_count = sum(1 for kw in medical_keywords if kw in text_lower)
        technical_count = sum(1 for kw in technical_keywords if kw in text_lower)
        
        max_count = max(business_count, medical_count, technical_count)
        
        if max_count >= 3:
            if medical_count == max_count:
                return "medical_vocab"
            elif technical_count == max_count:
                return "technical_vocab"
            elif business_count == max_count:
                return "business_vocab"
        
        # Check if multiple domains present
        domains_present = sum([
            business_count >= 2,
            medical_count >= 2,
            technical_count >= 2
        ])
        
        if domains_present >= 2:
            return "mixed_vocab"
        
        return "general_vocab"
    
    def normalize_text(self, text: str) -> str:
        """
        Apply basic Thai text normalization
        """
        if not self.thai_available or not text:
            return text
        
        try:
            # Apply PyThaiNLP normalization
            normalized = normalize(text)
            return normalized
        except Exception as e:
            print(f"Normalization error: {e}")
            return text


class MetadataGenerator:
    """Generates and manages metadata files"""
    
    def __init__(self, output_dir: str = "metadata"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_metadata(self, audio_path: str, 
                         audio_analysis: Dict,
                         transcription: Optional[Dict],
                         language_analysis: Optional[Dict]) -> Dict:
        """Generate complete metadata structure"""
        
        metadata = {
            'file_info': {
                'filename': Path(audio_path).name,
                'file_path': str(audio_path),
                'processed_at': datetime.now().isoformat(),
                'file_size_bytes': os.path.getsize(audio_path)
            },
            'audio_properties': {
                'duration_seconds': audio_analysis.get('duration', 0),
                'sample_rate': audio_analysis.get('sample_rate', 16000)
            },
            'automated_tags': {
                'noise_level': audio_analysis.get('noise_level', 'unknown'),
                'noise_level_confidence': audio_analysis.get('noise_confidence', 'high'),
                'snr_db': audio_analysis.get('snr_db', 0),
                'speech_clarity': audio_analysis.get('speech_clarity', 'unknown'),
                'speech_clarity_confidence': audio_analysis.get('clarity_confidence', 'medium'),
                'speaking_style_suggested': audio_analysis.get('speaking_style', 'unknown'),
                'speaking_style_confidence': 'low',  # Always low for automated
                'voice_activity_percentage': audio_analysis.get('voice_activity', 0)
            },
            'acoustic_features': audio_analysis.get('clarity_features', {}),
            'speaking_style_features': audio_analysis.get('style_features', {}),
            'text': language_analysis.get('normalized_text', '') if language_analysis else (transcription.get('text', '') if transcription else ''),
            'transcription_metadata': {
                'available': transcription is not None,
                'normalization_applied': language_analysis.get('normalization_applied', False) if language_analysis else False,
                'normalization_notes': language_analysis.get('normalization_notes', '') if language_analysis else '',
                'language_detected': transcription.get('language', 'th') if transcription else 'th'
            },
            'linguistic_analysis': {
                'code_switching': language_analysis.get('code_switching', 'unknown') if language_analysis else 'unknown',
                'vocabulary_type_suggested': language_analysis.get('vocabulary_type', 'general_vocab') if language_analysis else 'general_vocab',
                'vocabulary_confidence': 'low'  # Always low without manual review
            },
            'manual_review_required': {
                'speaker_gender': 'required',
                'dialect': 'required',
                'speaking_style_confirmation': 'required',
                'vocabulary_type_confirmation': 'required',
                'code_switching_confirmation': 'required'
            },
            'annotation_status': {
                'automated_complete': True,
                'human_review_complete': False,
                'human_annotator': None,
                'review_date': None
            },
            'notes': []
        }
        
        # Add confidence notes
        if audio_analysis.get('snr_db', 30) < 15:
            metadata['notes'].append('Low SNR detected - audio quality may affect transcription')
        
        if transcription and len(transcription.get('text', '')) < 10:
            metadata['notes'].append('Very short transcription - check for silence or audio issues')
        
        return metadata
    
    def save_metadata(self, metadata: Dict, audio_filename: str) -> str:
        """Save metadata to JSON file"""
        base_name = Path(audio_filename).stem
        output_path = self.output_dir / f"{base_name}_metadata.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return str(output_path)


class ThaiSTTAutoTagger:
    """Main class orchestrating the auto-tagging process"""
    
    def __init__(self, whisper_model: str = "medium", sample_rate: int = 16000):
        print_progress("Initializing Thai STT Auto-Tagger...", 0)
        
        # Check FFmpeg availability for MP3 support
        self._check_ffmpeg()
        
        self.audio_analyzer = AudioAnalyzer(sample_rate=sample_rate)
        print_progress("✓ Audio analyzer ready", 1)
        
        self.transcriber = SpeechTranscriber(model_name=whisper_model)
        if WHISPER_AVAILABLE:
            print_progress("✓ Transcriber ready", 1)
        
        self.language_analyzer = LanguageAnalyzer()
        if PYTHAINLP_AVAILABLE:
            print_progress("✓ Thai language analyzer ready", 1)
        else:
            print_progress("⚠ PyThaiNLP not available - text processing limited", 1)
            
        self.metadata_generator = MetadataGenerator()
        print_progress("✓ Metadata generator ready", 1)
        print()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        import subprocess
        import shutil
        
        # Check using shutil.which (more reliable)
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            print_progress(f"✓ FFmpeg found: {ffmpeg_path}", 1)
            return True
        
        # Fallback: try running ffmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_progress("✓ FFmpeg is available", 1)
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # FFmpeg not found
        print_progress("⚠ FFmpeg not found - MP3 support may be limited", 1)
        print_progress("  Install: https://ffmpeg.org/download.html", 1)
        print_progress("  Ubuntu/Debian: sudo apt-get install ffmpeg", 1)
        print_progress("  macOS: brew install ffmpeg", 1)
        print_progress("  Windows: Download from ffmpeg.org", 1)
        return False
    
    def process_file(self, audio_path: str, enable_transcription: bool = True) -> Dict:
        """Process a single audio file"""
        total_start = time.time()
        
        print(f"\n{'='*70}")
        print(f"Processing: {audio_path}")
        print(f"{'='*70}")
        
        # Validate file before processing
        if not Path(audio_path).exists():
            print(f"❌ ERROR: File not found: {audio_path}")
            raise FileNotFoundError(f"File not found: {audio_path}")
        
        file_size = Path(audio_path).stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        file_ext = Path(audio_path).suffix.lower()
        
        print_progress(f"File info:", 0)
        print_progress(f"Size: {file_size_mb:.2f} MB", 1)
        print_progress(f"Format: {file_ext}", 1)
        
        # Warn about large files
        if file_size_mb > 100:
            print_progress(f"⚠ Large file detected - loading may take longer", 1)
        
        # Warn about format
        if file_ext not in ['.mp3', '.wav', '.flac', '.m4a']:
            print_progress(f"⚠ Unusual format - may not load correctly", 1)
        
        timings = {}
        
        # Load audio
        print()
        print_progress("⏳ Loading audio file...", 0)
        start = time.time()
        try:
            y, sr = self.audio_analyzer.load_audio(audio_path)
            duration = len(y) / sr
            timings['load_audio'] = time.time() - start
            print_progress(f"✓ Loaded {duration:.2f}s audio in {timings['load_audio']:.2f}s", 1)
        except Exception as e:
            print()
            print(f"❌ FAILED TO LOAD AUDIO FILE")
            print(f"   File: {audio_path}")
            print(f"   Error: {str(e)}")
            raise
        
        # Analyze audio properties
        print_progress("⏳ Analyzing acoustic properties...", 0)
        
        # SNR calculation
        print_progress("Calculating Signal-to-Noise Ratio...", 1)
        start = time.time()
        snr_db = self.audio_analyzer.calculate_snr(y)
        noise_level = self.audio_analyzer.classify_noise_level(snr_db)
        timings['snr'] = time.time() - start
        print_progress(f"✓ SNR: {snr_db:.2f} dB → {noise_level} ({timings['snr']:.2f}s)", 2)
        
        # Speech clarity
        print_progress("Analyzing speech clarity features...", 1)
        start = time.time()
        clarity_features = self.audio_analyzer.analyze_speech_clarity(y, sr)
        speech_clarity = self.audio_analyzer.classify_speech_clarity(clarity_features, snr_db)
        timings['clarity'] = time.time() - start
        print_progress(f"✓ Speech Clarity: {speech_clarity} ({timings['clarity']:.2f}s)", 2)
        
        # Speaking style
        print_progress("Detecting speaking style patterns...", 1)
        start = time.time()
        style_features = self.audio_analyzer.analyze_speaking_style(y, sr)
        speaking_style = self.audio_analyzer.classify_speaking_style(style_features)
        timings['style'] = time.time() - start
        print_progress(f"✓ Style: {speaking_style} ({timings['style']:.2f}s)", 2)
        
        # Voice activity
        voice_activity = style_features['speech_percentage']
        print_progress(f"✓ Voice Activity: {voice_activity:.1f}%", 2)
        
        audio_analysis = {
            'duration': duration,
            'sample_rate': sr,
            'snr_db': snr_db,
            'noise_level': noise_level,
            'noise_confidence': 'high',
            'speech_clarity': speech_clarity,
            'clarity_confidence': 'medium',
            'speaking_style': speaking_style,
            'voice_activity': voice_activity,
            'clarity_features': clarity_features,
            'style_features': style_features
        }
        
        # Transcribe
        transcription = None
        language_analysis = None
        
        if enable_transcription and WHISPER_AVAILABLE:
            print_progress("⏳ Transcribing audio (this may take a while)...", 0)
            start = time.time()
            transcription = self.transcriber.transcribe(audio_path)
            timings['transcription'] = time.time() - start
            
            if transcription and transcription['text']:
                text = transcription['text']
                print_progress(f"✓ Transcribed in {timings['transcription']:.2f}s", 1)
                print_progress(f"Text preview: {text[:80]}...", 2)
                
                # Analyze language
                print_progress("⏳ Analyzing linguistic features...", 0)
                start = time.time()
                code_switching = self.language_analyzer.detect_code_switching(text)
                vocabulary_type = self.language_analyzer.analyze_vocabulary_type(text)
                normalized_text = self.language_analyzer.normalize_text(text)
                timings['linguistic'] = time.time() - start
                
                print_progress(f"✓ Code-Switching: {code_switching}", 1)
                print_progress(f"✓ Vocabulary: {vocabulary_type}", 1)
                print_progress(f"✓ Linguistic analysis done ({timings['linguistic']:.2f}s)", 1)
                
                language_analysis = {
                    'code_switching': code_switching,
                    'vocabulary_type': vocabulary_type,
                    'normalized_text': normalized_text,
                    'normalization_applied': normalized_text != text,
                    'normalization_notes': self._get_normalization_notes(text, normalized_text)
                }
        elif not enable_transcription:
            print_progress("⊘ Transcription disabled (skipped)", 0)
        else:
            print_progress("⊘ Transcription unavailable (Whisper not installed)", 0)
        
        # Generate metadata
        print_progress("⏳ Generating metadata...", 0)
        start = time.time()
        metadata = self.metadata_generator.generate_metadata(
            audio_path, audio_analysis, transcription, language_analysis
        )
        timings['metadata'] = time.time() - start
        print_progress(f"✓ Metadata generated ({timings['metadata']:.2f}s)", 1)
        
        # Save metadata
        print_progress("⏳ Saving metadata file...", 0)
        start = time.time()
        output_path = self.metadata_generator.save_metadata(
            metadata, Path(audio_path).name
        )
        timings['save'] = time.time() - start
        print_progress(f"✓ Saved to: {output_path} ({timings['save']:.2f}s)", 1)
        
        # Summary
        total_time = time.time() - total_start
        print(f"\n{'─'*70}")
        print(f"⏱️  TIMING SUMMARY:")
        print(f"{'─'*70}")
        print(f"  Audio Loading:      {timings.get('load_audio', 0):>6.2f}s")
        print(f"  SNR Analysis:       {timings.get('snr', 0):>6.2f}s")
        print(f"  Clarity Analysis:   {timings.get('clarity', 0):>6.2f}s")
        print(f"  Style Detection:    {timings.get('style', 0):>6.2f}s")
        if 'transcription' in timings:
            print(f"  Transcription:      {timings.get('transcription', 0):>6.2f}s")
            print(f"  Linguistic Analysis:{timings.get('linguistic', 0):>6.2f}s")
        print(f"  Metadata Gen/Save:  {timings.get('metadata', 0) + timings.get('save', 0):>6.2f}s")
        print(f"  {'─'*35}")
        print(f"  TOTAL TIME:         {total_time:>6.2f}s")
        print(f"{'─'*70}")
        
        return metadata
    
    def _get_normalization_notes(self, original: str, normalized: str) -> str:
        """Generate notes about what normalization did"""
        if original == normalized:
            return "No changes made - text is already in standard form"
        
        notes = []
        
        # Check what changed
        if len(original) != len(normalized):
            notes.append(f"Length changed: {len(original)} → {len(normalized)} characters")
        
        # Check for common normalizations
        import re
        
        # Numbers
        if re.search(r'\d', original) and original != normalized:
            notes.append("Numbers may have been normalized")
        
        # Whitespace
        if '  ' in original or '\n' in original or '\t' in original:
            notes.append("Whitespace standardized")
        
        # Zero-width characters
        if '\u200b' in original:
            notes.append("Zero-width spaces removed")
        
        if not notes:
            notes.append("Minor character standardization applied")
        
        return "; ".join(notes)
    
    def process_directory(self, input_dir: str, pattern: str = "*.mp3",
                         enable_transcription: bool = True) -> List[Dict]:
        """Process all audio files in a directory"""
        input_path = Path(input_dir)
        audio_files = list(input_path.glob(pattern))
        
        if not audio_files:
            print(f"\n❌ No audio files found matching pattern: {pattern}")
            print(f"   In directory: {input_path.absolute()}")
            return []
        
        total_start = time.time()
        print(f"\n{'='*70}")
        print(f"📁 BATCH PROCESSING")
        print(f"{'='*70}")
        print(f"Directory: {input_path.absolute()}")
        print(f"Pattern:   {pattern}")
        print(f"Found:     {len(audio_files)} files")
        print(f"Mode:      {'Full (with transcription)' if enable_transcription else 'Fast (audio only)'}")
        print(f"{'='*70}\n")
        
        results = []
        successful = 0
        failed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n{'█'*70}")
            print(f"📄 FILE {i}/{len(audio_files)}")
            print(f"{'█'*70}")
            
            try:
                metadata = self.process_file(str(audio_file), enable_transcription)
                results.append(metadata)
                successful += 1
            except Exception as e:
                failed += 1
                print(f"\n❌ ERROR processing {audio_file.name}")
                print(f"   Error: {str(e)}")
                import traceback
                traceback.print_exc()
                print(f"   Continuing with next file...")
        
        # Final summary
        total_time = time.time() - total_start
        print(f"\n{'='*70}")
        print(f"✅ BATCH PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"Total files:      {len(audio_files)}")
        print(f"Successful:       {successful} ✓")
        if failed > 0:
            print(f"Failed:           {failed} ✗")
        print(f"Total time:       {total_time:.2f}s ({total_time/60:.1f} minutes)")
        print(f"Average per file: {total_time/len(audio_files):.2f}s")
        print(f"Output directory: metadata/")
        print(f"{'='*70}\n")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Automated tagging system for Thai STT dataset"
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing audio files'
    )
    parser.add_argument(
        '--file', '-f',
        help='Process single file (optional)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Process all MP3 files in directory'
    )
    parser.add_argument(
        '--output', '-o',
        default='metadata',
        help='Output directory for metadata files (default: metadata)'
    )
    parser.add_argument(
        '--no-transcription',
        action='store_true',
        help='Disable transcription (faster processing)'
    )
    parser.add_argument(
        '--whisper-model',
        default='medium',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: medium)'
    )
    parser.add_argument(
        '--pattern',
        default='*.mp3',
        help='File pattern to match (default: *.mp3)'
    )
    
    args = parser.parse_args()
    
    # Initialize tagger
    tagger = ThaiSTTAutoTagger(
        whisper_model=args.whisper_model,
        sample_rate=16000
    )
    
    # Update output directory
    tagger.metadata_generator.output_dir = Path(args.output)
    tagger.metadata_generator.output_dir.mkdir(parents=True, exist_ok=True)
    
    enable_transcription = not args.no_transcription
    
    # Process files
    if args.file:
        # Process single file
        file_path = Path(args.input) / args.file
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return
        
        tagger.process_file(str(file_path), enable_transcription)
    
    elif args.all:
        # Process all files
        tagger.process_directory(
            args.input,
            pattern=args.pattern,
            enable_transcription=enable_transcription
        )
    
    else:
        print("Error: Must specify either --file or --all")
        parser.print_help()


if __name__ == "__main__":
    main()
