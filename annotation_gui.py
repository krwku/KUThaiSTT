#!/usr/bin/env python3
"""
Thai STT Annotation GUI - Fixed and Enhanced Version

A graphical user interface for manual annotation of Thai speech-to-text metadata.
Allows annotators to review and edit automated tags with audio playback.

Improvements:
- Fullscreen resizes internal components properly
- Helper text for Speaking Style and Vocabulary Type
- Larger transcribed text display
- Review status tracking with date/time
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path
from typing import Dict, List, Optional
import os
from datetime import datetime

# Try to import audio playback
try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Warning: pygame not installed - audio playback disabled")
    print("Install with: pip install pygame")


# Helper text for annotation fields
HELPER_TEXT = {
    'code_switching': """
HOW TO DECIDE:

• NO CODE-SWITCHING:
  - Pure Thai throughout entire speech
  - No English or other foreign words
  - Only traditional Thai vocabulary
  Example: "วันนี้อากาศดีมาก ผมไปตลาดซื้อของ"

• CODE-SWITCHING (Yes):
  - ANY English or foreign words present
  - Even a single foreign word counts
  - Mixed Thai and English/foreign language
  Examples: 
    - "ผมมี meeting ตอนบ่ายสองโมง" (one word)
    - "Yesterday ผม send email ไป" (multiple words)
    
Simple rule: If you hear ANY non-Thai words → Code-Switching = Yes
""",

    'speaking_style': """
HOW TO DECIDE:

• READ SPEECH:
  - Very smooth, consistent pacing
  - No hesitations or "um"/"uh" sounds
  - Formal tone, complete sentences
  - No false starts or corrections
  Example: News reading, scripted presentations

• SPONTANEOUS SPEECH:
  - Natural pauses and thinking sounds (เอ่อ, อืม)
  - Single person speaking naturally
  - May include mid-sentence corrections
  - Less formal, conversational tone
  Example: Interviews, vlogs, casual monologues

• CONVERSATIONAL:
  - Multiple speakers present
  - Turn-taking and responses
  - May have interruptions or overlaps
  Example: Dialogues, meetings, phone calls
""",
    
    'vocabulary_type': """
HOW TO DECIDE:

• GENERAL VOCAB:
  - Everyday language and common topics
  - No specialized terminology
  Example: "ผมไปตลาดซื้อของ" (casual conversation)

• BUSINESS VOCAB:
  - Business, finance, management terms
  - Keywords: ROI, stakeholder, quarter, profit
  Example: "ผลประกอบการไตรมาสนี้เพิ่มขึ้น"

• MEDICAL VOCAB:
  - Healthcare, medical terminology
  - Body parts, symptoms, treatments
  Example: "ผู้ป่วยมีอาการปวดศีรษะและไข้สูง"

• TECHNICAL VOCAB:
  - Engineering, IT, scientific terms
  - Programming, technical processes
  Example: "เราต้อง deploy code ใหม่ในเซิร์ฟเวอร์"

• MIXED VOCAB:
  - Spans multiple specialized domains
  - Mix of technical and general language
  Example: Business + Medical, or Tech + General
"""
}


class AnnotationGUI:
    """Main GUI application for annotation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Thai STT Annotation Tool")
        self.root.geometry("1400x900")
        
        # Data
        self.metadata_files: List[Path] = []
        self.current_file: Optional[Path] = None
        self.current_data: Optional[Dict] = None
        self.modified = False
        self.edit_mode = "partial"  # "partial" or "full"
        
        # Audio
        self.current_audio_path: Optional[str] = None
        
        # Track widgets for resizing
        self.resizable_widgets = []
        
        # Setup GUI
        self.setup_ui()
        self.load_metadata_list()
        
        # Bind window state change for fullscreen
        self.root.bind('<Configure>', self.on_window_configure)
        
    def on_window_configure(self, event):
        """Handle window resize/fullscreen"""
        # This is called on any window configuration change
        # You can add specific resize logic here if needed
        pass
        
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Metadata Directory", command=self.open_directory)
        file_menu.add_command(label="Reload File List", command=self.load_metadata_list)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label="Save and Next", command=self.save_and_next, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen, accelerator="F11")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_current())
        self.root.bind('<Control-n>', lambda e: self.save_and_next())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container with proper weight for resizing
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.main_container = main_container
        
        # Left panel - File list
        self.setup_left_panel(main_container)
        
        # Right panel - Annotation fields
        self.setup_right_panel(main_container)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def setup_left_panel(self, parent):
        """Setup left panel with file list"""
        left_frame = ttk.Frame(parent, width=300)
        parent.add(left_frame, weight=1)
        
        # Header
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Metadata Files", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Refresh", command=self.load_metadata_list, width=8).pack(side=tk.RIGHT)
        
        # Stats
        self.stats_label = ttk.Label(left_frame, text="Files: 0 | Reviewed: 0")
        self.stats_label.pack(fill=tk.X, padx=5)
        
        # Search/filter
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_file_list())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # File list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                        selectmode=tk.SINGLE, font=('Courier', 9))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Legend
        legend_frame = ttk.LabelFrame(left_frame, text="Status", padding=5)
        legend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(legend_frame, text="✓ = Reviewed", foreground="green").pack(anchor=tk.W)
        ttk.Label(legend_frame, text="○ = Pending", foreground="gray").pack(anchor=tk.W)
    
    def setup_right_panel(self, parent):
        """Setup right panel with annotation fields"""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=3)
        
        # Top toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Edit mode toggle
        mode_frame = ttk.LabelFrame(toolbar, text="Edit Mode", padding=5)
        mode_frame.pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value="partial")
        ttk.Radiobutton(mode_frame, text="Partial (Manual Fields Only)", 
                       variable=self.mode_var, value="partial",
                       command=self.change_edit_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Full (All Fields)", 
                       variable=self.mode_var, value="full",
                       command=self.change_edit_mode).pack(side=tk.LEFT, padx=5)
        
        # Audio controls
        audio_frame = ttk.LabelFrame(toolbar, text="Audio", padding=5)
        audio_frame.pack(side=tk.LEFT, padx=5)
        
        self.play_button = ttk.Button(audio_frame, text="▶ Play", 
                                      command=self.play_audio, width=10)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(audio_frame, text="■ Stop", 
                                      command=self.stop_audio, width=10)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        if not AUDIO_AVAILABLE:
            self.play_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
        
        # Save buttons
        save_frame = ttk.Frame(toolbar)
        save_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(save_frame, text="💾 Save", command=self.save_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_frame, text="💾 Save & Next", command=self.save_and_next).pack(side=tk.LEFT, padx=2)
        
        # Create a horizontal paned window for content and helper
        content_paned = ttk.PanedWindow(right_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: Scrollable content area
        canvas_frame = ttk.Frame(content_paned)
        content_paned.add(canvas_frame, weight=3)
        
        canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.content_frame = ttk.Frame(canvas)
        self.content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Right side: Helper panel
        helper_frame = ttk.LabelFrame(content_paned, text="Helper Guide", padding=10)
        content_paned.add(helper_frame, weight=1)
        
        self.helper_text = tk.Text(helper_frame, wrap=tk.WORD, font=('Arial', 9),
                                   bg='#f0f0f0', relief=tk.FLAT, padx=10, pady=10)
        self.helper_text.pack(fill=tk.BOTH, expand=True)
        self.helper_text.config(state=tk.DISABLED)
        
        # Initial message
        ttk.Label(self.content_frame, text="Select a file from the list to begin annotation",
                 font=('Arial', 12), foreground='gray').pack(pady=50)
    
    def show_helper_text(self, field_type):
        """Show helper text for a specific field"""
        if field_type in HELPER_TEXT:
            self.helper_text.config(state=tk.NORMAL)
            self.helper_text.delete('1.0', tk.END)
            self.helper_text.insert('1.0', HELPER_TEXT[field_type])
            self.helper_text.config(state=tk.DISABLED)
        else:
            self.helper_text.config(state=tk.NORMAL)
            self.helper_text.delete('1.0', tk.END)
            self.helper_text.insert('1.0', "Select a field to see helpful guidelines...")
            self.helper_text.config(state=tk.DISABLED)
    
    def load_metadata_list(self):
        """Load list of metadata files"""
        metadata_dir = Path("metadata")
        if not metadata_dir.exists():
            messagebox.showerror("Error", "Metadata directory not found!\n\nExpected: ./metadata/")
            return
        
        self.metadata_files = sorted(metadata_dir.glob("*.json"))
        self.update_file_list()
        self.update_stats()
    
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)
        
        filter_text = self.search_var.get().lower()
        
        for meta_file in self.metadata_files:
            if filter_text and filter_text not in meta_file.name.lower():
                continue
            
            # Check if reviewed
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    reviewed = data.get('annotation_status', {}).get('human_review_complete', False)
                    review_date = data.get('annotation_status', {}).get('review_date', '')
                    
                    if reviewed and review_date:
                        # Format date nicely
                        try:
                            dt = datetime.fromisoformat(review_date)
                            date_str = dt.strftime("%Y-%m-%d %H:%M")
                            icon = "✓"
                            display_name = f"{icon} {meta_file.name} [{date_str}]"
                        except:
                            icon = "✓"
                            display_name = f"{icon} {meta_file.name}"
                    elif reviewed:
                        icon = "✓"
                        display_name = f"{icon} {meta_file.name}"
                    else:
                        icon = "○"
                        display_name = f"{icon} {meta_file.name}"
            except:
                icon = "○"
                display_name = f"{icon} {meta_file.name}"
            
            self.file_listbox.insert(tk.END, display_name)
    
    def filter_file_list(self):
        """Filter file list based on search text"""
        self.update_file_list()
    
    def update_stats(self):
        """Update statistics label"""
        total = len(self.metadata_files)
        reviewed = 0
        
        for meta_file in self.metadata_files:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('annotation_status', {}).get('human_review_complete', False):
                        reviewed += 1
            except:
                pass
        
        self.stats_label.config(text=f"Files: {total} | Reviewed: {reviewed} ({reviewed/total*100:.1f}%)" if total > 0 else "Files: 0")
    
    def on_file_select(self, event):
        """Handle file selection"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        # Check for unsaved changes
        if self.modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                  "Save changes before switching files?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_current()
        
        # Get actual file (strip icon and date info)
        idx = selection[0]
        display_name = self.file_listbox.get(idx)
        
        # Extract just the filename
        # Format: "✓ filename.json [date]" or "○ filename.json"
        # Remove icon and space at start
        filename = display_name[2:] if len(display_name) > 2 else display_name
        
        # Remove date part if present
        if ' [' in filename:
            filename = filename.split(' [')[0]
        
        # Find the actual file
        for meta_file in self.metadata_files:
            if meta_file.name == filename:
                self.current_file = meta_file
                break
        
        if not self.current_file:
            return
        
        # Load metadata
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            
            self.modified = False
            self.display_annotation_fields()
            self.status_var.set(f"Loaded: {self.current_file.name}")
            
            # Find audio file
            audio_dir = Path("data")
            audio_filename = self.current_data.get('file_info', {}).get('filename', '')
            if audio_filename:
                audio_path = audio_dir / audio_filename
                if audio_path.exists():
                    self.current_audio_path = str(audio_path)
                else:
                    self.current_audio_path = None
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file:\n{str(e)}")
    
    def display_annotation_fields(self):
        """Display annotation fields for current file"""
        # Clear existing widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.field_widgets = {}
        
        if not self.current_data:
            return
        
        # Title
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(title_frame, text=f"Annotating: {self.current_file.name}", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Review Status Badge
        reviewed = self.current_data.get('annotation_status', {}).get('human_review_complete', False)
        review_date = self.current_data.get('annotation_status', {}).get('review_date', '')
        reviewer = self.current_data.get('annotation_status', {}).get('human_annotator', '')
        
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(side=tk.RIGHT)
        
        if reviewed:
            status_label = ttk.Label(status_frame, text="✓ REVIEWED", 
                                     font=('Arial', 10, 'bold'), foreground='green')
            status_label.pack()
            if review_date:
                try:
                    dt = datetime.fromisoformat(review_date)
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                    ttk.Label(status_frame, text=f"Date: {date_str}", 
                             font=('Arial', 8), foreground='gray').pack()
                except:
                    pass
            if reviewer:
                ttk.Label(status_frame, text=f"By: {reviewer}", 
                         font=('Arial', 8), foreground='gray').pack()
        else:
            ttk.Label(status_frame, text="○ PENDING REVIEW", 
                     font=('Arial', 10, 'bold'), foreground='gray').pack()
        
        ttk.Separator(self.content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        # File info
        info_frame = ttk.LabelFrame(self.content_frame, text="File Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        file_info = self.current_data.get('file_info', {})
        audio_props = self.current_data.get('audio_properties', {})
        ttk.Label(info_frame, text=f"Filename: {file_info.get('filename', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Duration: {audio_props.get('duration_seconds', 0):.2f}s").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Sample Rate: {audio_props.get('sample_rate', 0)} Hz").pack(anchor=tk.W)
        
        # Transcription section - LARGER DISPLAY
        trans_frame = ttk.LabelFrame(self.content_frame, text="Transcription", padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Get transcription text
        text_value = self.current_data.get('text', '')
        if not text_value:
            # Fallback to old structure
            text_value = self.current_data.get('transcription', {}).get('text', 'No transcription available')
        
        # Create larger text display with scroll
        trans_text_frame = ttk.Frame(trans_frame)
        trans_text_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scrollbar = ttk.Scrollbar(trans_text_frame)
        trans_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        trans_text = tk.Text(trans_text_frame, wrap=tk.WORD, height=8, font=('Arial', 12),
                            yscrollcommand=trans_scrollbar.set, relief=tk.SOLID, borderwidth=1)
        trans_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scrollbar.config(command=trans_text.yview)
        
        trans_text.insert('1.0', text_value)
        trans_text.config(state=tk.DISABLED, bg='#f9f9f9')
        
        # Automated tags (read-only or editable based on mode)
        auto_frame = ttk.LabelFrame(self.content_frame, text="Automated Tags", padding=10)
        auto_frame.pack(fill=tk.X, padx=10, pady=5)
        
        automated = self.current_data.get('automated_tags', {})
        linguistic = self.current_data.get('linguistic_analysis', {})
        
        if self.edit_mode == "full":
            # Show all fields as editable
            self.add_field(auto_frame, "Noise Level", "noise_level", 
                          automated.get('noise_level', 'unknown'),
                          ['low_noise', 'medium_noise', 'high_noise'])
            
            self.add_field(auto_frame, "Speech Clarity", "speech_clarity",
                          automated.get('speech_clarity', 'unknown'),
                          ['clear_speech', 'muffled_speech', 'distorted_speech'])
        else:
            # Show as read-only labels
            ttk.Label(auto_frame, text=f"Noise Level: {automated.get('noise_level', 'N/A')}").pack(anchor=tk.W, pady=2)
            ttk.Label(auto_frame, text=f"Speech Clarity: {automated.get('speech_clarity', 'N/A')}").pack(anchor=tk.W, pady=2)
            ttk.Label(auto_frame, text=f"Code-Switching (AI suggestion): {linguistic.get('code_switching', 'N/A')}").pack(anchor=tk.W, pady=2)
        
        # Manual annotation fields (always editable)
        manual_frame = ttk.LabelFrame(self.content_frame, text="Manual Annotations (Required *)", padding=10)
        manual_frame.pack(fill=tk.X, padx=10, pady=5)
        
        manual = self.current_data.get('manual_annotations', {})
        
        # Speaker Gender
        gender_frame = ttk.Frame(manual_frame)
        gender_frame.pack(fill=tk.X, pady=5)
        self.add_field(gender_frame, "Speaker Gender *", "speaker_gender",
                      manual.get('speaker_gender', automated.get('speaker_gender', '')),
                      ['male', 'female', 'child', 'unknown'])
        
        # Code-Switching with helper button
        code_frame = ttk.Frame(manual_frame)
        code_frame.pack(fill=tk.X, pady=5)
        self.add_field(code_frame, "Code-Switching *", "code_switching",
                      manual.get('code_switching', linguistic.get('code_switching', automated.get('code_switching', ''))),
                      ['no_code_switching', 'code_switching'],
                      show_helper='code_switching')
        
        # Speaking Style with helper button
        style_frame = ttk.Frame(manual_frame)
        style_frame.pack(fill=tk.X, pady=5)
        self.add_field(style_frame, "Speaking Style *", "speaking_style",
                      manual.get('speaking_style', automated.get('speaking_style', '')),
                      ['read_speech', 'spontaneous_speech', 'conversational'],
                      show_helper='speaking_style')
        
        # Dialect
        dialect_frame = ttk.Frame(manual_frame)
        dialect_frame.pack(fill=tk.X, pady=5)
        self.add_field(dialect_frame, "Dialect *", "dialect",
                      manual.get('dialect', automated.get('dialect', '')),
                      ['central_thai', 'northern_thai', 'isan_thai', 'southern_thai', 'other_thai_dialect'])
        
        # Vocabulary Type with helper button
        vocab_frame = ttk.Frame(manual_frame)
        vocab_frame.pack(fill=tk.X, pady=5)
        self.add_field(vocab_frame, "Vocabulary Type *", "vocabulary_type",
                      manual.get('vocabulary_type', linguistic.get('vocabulary_type_suggested', automated.get('vocabulary_type', ''))),
                      ['general_vocab', 'business_vocab', 'medical_vocab', 'technical_vocab', 'mixed_vocab'],
                      show_helper='vocabulary_type')
        
        # Notes
        notes_frame = ttk.LabelFrame(self.content_frame, text="Notes (Optional)", padding=10)
        notes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        notes_text.pack(fill=tk.X, expand=True)
        
        existing_notes = self.current_data.get('notes', [])
        if existing_notes:
            notes_text.insert('1.0', '\n'.join(existing_notes))
        
        self.field_widgets['notes'] = notes_text
        notes_text.bind('<KeyRelease>', lambda e: self.mark_modified())
        
        # Show initial helper text
        self.show_helper_text(None)
    
    def add_field(self, parent, label, field_name, current_value, options, show_helper=None):
        """Add a selection field"""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill=tk.X, pady=2)
        
        label_frame = ttk.Frame(field_frame)
        label_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(label_frame, text=f"{label}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        # Helper button if specified
        if show_helper:
            help_btn = ttk.Button(label_frame, text="?", width=2,
                                 command=lambda: self.show_helper_text(show_helper))
            help_btn.pack(side=tk.LEFT, padx=2)
        
        # Ensure current_value is in options, otherwise use first option or empty
        if current_value and current_value not in options:
            print(f"Warning: Value '{current_value}' not in options for {field_name}. Using empty.")
            current_value = ''
        
        var = tk.StringVar(value=current_value if current_value else '')
        self.field_widgets[field_name] = var
        
        combo = ttk.Combobox(field_frame, textvariable=var, values=options, 
                            state='readonly', width=30)
        combo.pack(side=tk.LEFT, padx=5)
        
        # Set the current selection by index if value exists
        if current_value and current_value in options:
            try:
                index = options.index(current_value)
                combo.current(index)
            except ValueError:
                pass
        
        combo.bind('<<ComboboxSelected>>', lambda e: self.mark_modified())
        
        # Show helper when field is focused
        if show_helper:
            combo.bind('<FocusIn>', lambda e: self.show_helper_text(show_helper))
    
    def mark_modified(self):
        """Mark current file as modified"""
        self.modified = True
        if not self.status_var.get().endswith(" *"):
            self.status_var.set(self.status_var.get() + " *")
    
    def change_edit_mode(self):
        """Change edit mode"""
        self.edit_mode = self.mode_var.get()
        if self.current_data:
            self.display_annotation_fields()
    
    def collect_annotations(self) -> Dict:
        """Collect all annotations from fields"""
        annotations = {}
        
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, tk.StringVar):
                annotations[field_name] = widget.get()
            elif isinstance(widget, tk.Text):
                value = widget.get('1.0', tk.END).strip()
                if field_name == 'notes':
                    annotations[field_name] = [line for line in value.split('\n') if line.strip()]
                else:
                    annotations[field_name] = value
            elif isinstance(widget, ttk.Entry):
                annotations[field_name] = widget.get()
        
        return annotations
    
    def save_current(self):
        """Save current annotations"""
        if not self.current_file or not self.current_data:
            return
        
        # Collect annotations
        annotations = self.collect_annotations()
        
        # Ensure proper structure
        if 'automated_tags' not in self.current_data:
            self.current_data['automated_tags'] = {}
        if 'manual_annotations' not in self.current_data:
            self.current_data['manual_annotations'] = {}
        if 'annotation_status' not in self.current_data:
            self.current_data['annotation_status'] = {}
        
        # Update based on edit mode
        for key, value in annotations.items():
            if key == 'notes':
                self.current_data['notes'] = value
            elif self.edit_mode == "full" and key in ['noise_level', 'speech_clarity']:
                # In full mode, can override these automated tags only
                self.current_data['automated_tags'][key] = value
            else:
                # Manual annotations (includes speaker_gender, code_switching, speaking_style, dialect, vocabulary_type)
                self.current_data['manual_annotations'][key] = value
        
        # Update annotation status with timestamp
        self.current_data['annotation_status']['human_review_complete'] = True
        self.current_data['annotation_status']['human_annotator'] = os.getlogin()
        self.current_data['annotation_status']['review_date'] = datetime.now().isoformat()
        
        # Save to file
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            
            self.modified = False
            self.status_var.set(f"Saved: {self.current_file.name}")
            self.update_file_list()
            self.update_stats()
            
            # Refresh display to show updated review status
            self.display_annotation_fields()
            
            messagebox.showinfo("Saved", "Annotations saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save:\n{str(e)}")
    
    def save_and_next(self):
        """Save and move to next file"""
        self.save_current()
        
        # Find next file
        selection = self.file_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < self.file_listbox.size() - 1:
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(idx + 1)
                self.file_listbox.see(idx + 1)
                self.on_file_select(None)
    
    def play_audio(self):
        """Play audio file"""
        if not AUDIO_AVAILABLE:
            messagebox.showinfo("Audio Unavailable", "Install pygame for audio playback:\npip install pygame")
            return
        
        if not self.current_audio_path or not Path(self.current_audio_path).exists():
            messagebox.showwarning("Audio Not Found", 
                                  "Audio file not found. Make sure it's in the 'data' directory.")
            return
        
        try:
            pygame.mixer.music.load(self.current_audio_path)
            pygame.mixer.music.play()
            self.status_var.set("Playing audio...")
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to play audio:\n{str(e)}")
    
    def stop_audio(self):
        """Stop audio playback"""
        if AUDIO_AVAILABLE:
            pygame.mixer.music.stop()
            self.status_var.set("Audio stopped")
    
    def open_directory(self):
        """Open a different metadata directory"""
        directory = filedialog.askdirectory(title="Select Metadata Directory")
        if directory:
            os.chdir(directory)
            self.load_metadata_list()
    
    def show_instructions(self):
        """Show instructions dialog"""
        instructions = """
Thai STT Annotation Tool - Instructions

GETTING STARTED:
1. Audio files should be in 'data' directory
2. Metadata files should be in 'metadata' directory
3. Select a file from the left panel to begin

EDIT MODES:
• Partial Mode (Default): Shows only fields requiring manual review
  - Speaker gender, dialect, speaking style, vocabulary type
  - Quick annotation for essential fields only

• Full Mode: Shows all fields including automated tags
  - Use for detailed review or corrections
  - Can override any automated classification

REQUIRED FIELDS (marked with *):
• Code-Switching: Confirm or change AI suggestion (? for help)
• Speaking Style: Confirm or change AI suggestion (? for help)
• Dialect: central_thai/northern_thai/isan_thai/southern_thai
• Vocabulary Type: Confirm or change AI suggestion (? for help)

HELPER BUTTONS (?):
• Click the "?" button next to Code-Switching, Speaking Style or Vocabulary Type
• Detailed guidelines appear in the right panel
• Helps you make accurate classifications

AUDIO PLAYBACK:
• Click ▶ Play to listen to the audio
• Click ■ Stop to stop playback
• Make sure audio file exists in 'data' directory

REVIEW STATUS:
• Files marked ✓ are reviewed (shows date/time)
• Files marked ○ are pending review
• Your annotations are timestamped automatically

SAVING:
• Ctrl+S: Save current file
• Ctrl+N: Save and move to next file
• F11: Toggle fullscreen
• 💾 Save button: Save without moving
• 💾 Save & Next button: Save and go to next

STATUS INDICATORS:
• ✓ = Reviewed (green) with timestamp
• ○ = Pending review (gray)
• * = Unsaved changes

NOTES:
• Add any observations or issues in the Notes section
• Notes are saved with the annotations
• Use for documenting unusual cases or problems
        """
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Instructions")
        dialog.geometry("700x600")
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                           "Thai STT Annotation Tool\nVersion 1.1 (Enhanced)\n\n"
                           "A GUI for manual annotation of Thai speech-to-text metadata.\n\n"
                           "Features:\n"
                           "- Fullscreen support with proper resizing\n"
                           "- Helper text for decision-making\n"
                           "- Larger transcription display\n"
                           "- Review status tracking with timestamps\n\n"
                           "Part of the Thai STT Benchmark Dataset project.")
    
    def on_closing(self):
        """Handle window closing"""
        if self.modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                  "Save changes before exiting?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_current()
        
        if AUDIO_AVAILABLE:
            pygame.mixer.quit()
        
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AnnotationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
