import os
import customtkinter as ctk
from tkinter import filedialog, Listbox
from src.constants.app_constants import PLAY_BUTTON_LABEL, LOAD_BUTTON_LABEL


class AudioPlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.play_pause_btn = None
        self.load_btn = None
        self.controller = controller
        self.file_list = []  # List to hold the file names
        self.audio_listbox = None  # Listbox to display files
        self.folder_path = ''
        self.current_time_label = None
        self.total_time_label = None
        self.progress_slider = None
        self.slider_updating = False  # To prevent updating the slider during manual change

        self.create_ui()

    def create_ui(self):
        """Create the UI for loading and selecting audio files."""

        # Button to load audio files from folder
        self.load_btn = ctk.CTkButton(master=self, text=LOAD_BUTTON_LABEL, command=self.on_load_folder)
        self.load_btn.pack(pady=10)

        # Listbox to display audio files
        self.audio_listbox = Listbox(self, height=20, width=50)
        self.audio_listbox.pack(pady=10)
        self.audio_listbox.bind('<<ListboxSelect>>', self.on_select_audio)

        # Button to play selected audio
        self.play_pause_btn = ctk.CTkButton(master=self, text=PLAY_BUTTON_LABEL, command=self.on_play_audio)
        self.play_pause_btn.pack(pady=10)

        # Progress bar (slider) and time labels
        self.create_progress_bar()

    def on_load_folder(self):
        """Load audio files from a folder and display in the listbox."""
        self.folder_path = filedialog.askdirectory()  # Prompt user to select folder
        if self.folder_path:
            self.file_list = [f for f in os.listdir(self.folder_path) if f.endswith(".wav")]
            self.audio_listbox.delete(0, 'end')  # Clear current list
            for file in self.file_list:
                self.audio_listbox.insert('end', file)  # Add files to the listbox

    def on_select_audio(self, event):
        """Handle selection of an audio file from the list."""
        selected_index = self.audio_listbox.curselection()
        if selected_index:
            selected_file = self.file_list[selected_index[0]]
            self.controller.load_audio(os.path.join(self.folder_path, selected_file))

    def on_play_audio(self):
        """Play the selected audio file."""
        self.controller.play_audio()

    def create_progress_bar(self):
        """Create the progress bar and time labels."""
        self.current_time_label = ctk.CTkLabel(master=self, text="00:00")
        self.current_time_label.pack(side="left", padx=5)

        self.progress_slider = ctk.CTkSlider(master=self, from_=0, to=100, command=self.on_slider_change)
        self.progress_slider.pack(fill="x", padx=10, pady=10)

        self.total_time_label = ctk.CTkLabel(master=self, text="00:00")
        self.total_time_label.pack(side="right", padx=5)

    def update_progress_bar(self, current_time, total_time):
        """Update the progress bar and time labels."""
        self.slider_updating = True
        self.progress_slider.set(current_time / total_time * 100)
        self.current_time_label.configure(text=self.format_time(current_time))
        self.total_time_label.configure(text=self.format_time(total_time))
        self.slider_updating = False

    def format_time(self, seconds):
        """Convert seconds to a MM:SS string format."""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def on_slider_change(self, value):
        """Handle manual slider change."""
        if not self.slider_updating and self.controller.model.is_playing:
            # Seek to the corresponding position in the audio based on slider value
            total_time = self.controller.model.get_audio_duration()
            new_time = value / 100 * total_time
            self.controller.seek_audio(new_time)
