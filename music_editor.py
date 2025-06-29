import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import pygame.mixer
import numpy as np
from scipy.io import wavfile
import librosa
import soundfile as sf
import threading
import os

class MusicEditor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Music Editor & Mixer")
        self.window.geometry("1200x800")
        self.window.configure(bg='#1A1A1A')
        
        pygame.init()
        pygame.mixer.init()
        
        self.current_file = None
        self.audio_data = None
        self.sample_rate = None
        self.is_playing = False
        self.current_position = 0
        
        self.create_gui()
        
    def create_gui(self):
        # Main Controls
        controls = tk.Frame(self.window, bg='#1A1A1A')
        controls.pack(pady=10)
        
        ttk.Button(controls, text="Load Audio", command=self.load_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Play/Pause", command=self.toggle_play).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Stop", command=self.stop_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Save", command=self.save_audio).pack(side=tk.LEFT, padx=5)
        
        # Effects Frame
        effects = tk.LabelFrame(self.window, text="Audio Effects", bg='#2D2D2D', fg='white')
        effects.pack(pady=10, padx=10, fill=tk.X)
        
        # Volume Control
        volume_frame = tk.Frame(effects, bg='#2D2D2D')
        volume_frame.pack(pady=5, fill=tk.X)
        tk.Label(volume_frame, text="Volume:", bg='#2D2D2D', fg='white').pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=200)
        self.volume_scale.set(1.0)
        self.volume_scale.pack(side=tk.LEFT, padx=5)
        
        # Bass Boost
        bass_frame = tk.Frame(effects, bg='#2D2D2D')
        bass_frame.pack(pady=5, fill=tk.X)
        tk.Label(bass_frame, text="Bass Boost:", bg='#2D2D2D', fg='white').pack(side=tk.LEFT, padx=5)
        self.bass_scale = ttk.Scale(bass_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=200)
        self.bass_scale.set(1.0)
        self.bass_scale.pack(side=tk.LEFT, padx=5)
        
        # Treble
        treble_frame = tk.Frame(effects, bg='#2D2D2D')
        treble_frame.pack(pady=5, fill=tk.X)
        tk.Label(treble_frame, text="Treble:", bg='#2D2D2D', fg='white').pack(side=tk.LEFT, padx=5)
        self.treble_scale = ttk.Scale(treble_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=200)
        self.treble_scale.set(1.0)
        self.treble_scale.pack(side=tk.LEFT, padx=5)
        
        # Echo
        echo_frame = tk.Frame(effects, bg='#2D2D2D')
        echo_frame.pack(pady=5, fill=tk.X)
        tk.Label(echo_frame, text="Echo:", bg='#2D2D2D', fg='white').pack(side=tk.LEFT, padx=5)
        self.echo_scale = ttk.Scale(echo_frame, from_=0, to=1, orient=tk.HORIZONTAL, length=200)
        self.echo_scale.set(0)
        self.echo_scale.pack(side=tk.LEFT, padx=5)
        
        # Apply Effects Button
        ttk.Button(effects, text="Apply Effects", command=self.apply_effects).pack(pady=10)
        
        # Waveform Display
        self.waveform_canvas = tk.Canvas(self.window, bg='#1A1A1A', height=200)
        self.waveform_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status = tk.Label(self.window, textvariable=self.status_var, bg='#1A1A1A', fg='white')
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            try:
                self.current_file = file_path
                self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
                self.draw_waveform()
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load audio: {str(e)}")
                
    def draw_waveform(self):
        if self.audio_data is not None:
            self.waveform_canvas.delete("all")
            width = self.waveform_canvas.winfo_width()
            height = self.waveform_canvas.winfo_height()
            
            # Downsample for display
            samples = len(self.audio_data)
            points_per_pixel = max(1, samples // width)
            data = self.audio_data[::points_per_pixel]
            
            # Draw waveform
            for i in range(len(data)-1):
                x1 = i
                y1 = height//2 + (data[i] * height//2)
                x2 = i + 1
                y2 = height//2 + (data[i+1] * height//2)
                self.waveform_canvas.create_line(x1, y1, x2, y2, fill='#00FF00')
                
    def apply_effects(self):
        if self.audio_data is None:
            return
            
        # Create a copy of the original audio
        modified_audio = self.audio_data.copy()
        
        # Apply volume
        volume = self.volume_scale.get()
        modified_audio *= volume
        
        # Apply bass boost (simple low-shelf filter)
        if self.bass_scale.get() != 1.0:
            bass_boost = self.bass_scale.get()
            y_bass = librosa.effects.preemphasis(modified_audio, coef=-0.25)
            modified_audio = modified_audio + (y_bass * (bass_boost - 1))
            
        # Apply treble (simple high-shelf filter)
        if self.treble_scale.get() != 1.0:
            treble_boost = self.treble_scale.get()
            y_treble = librosa.effects.preemphasis(modified_audio)
            modified_audio = modified_audio + (y_treble * (treble_boost - 1))
            
        # Apply echo
        if self.echo_scale.get() > 0:
            echo_delay = int(self.sample_rate * 0.3)  # 300ms delay
            echo_strength = self.echo_scale.get()
            echo = np.zeros_like(modified_audio)
            echo[echo_delay:] = modified_audio[:-echo_delay] * echo_strength
            modified_audio += echo
            
        # Normalize
        modified_audio = np.clip(modified_audio, -1, 1)
        
        self.audio_data = modified_audio
        self.draw_waveform()
        self.status_var.set("Effects applied")
        
    def toggle_play(self):
        if self.audio_data is None:
            return
            
        if not self.is_playing:
            # Convert to audio file format pygame can play
            temp_file = "temp_audio.wav"
            sf.write(temp_file, self.audio_data, self.sample_rate)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.status_var.set("Playing")
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.status_var.set("Paused")
            
    def stop_audio(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.status_var.set("Stopped")
            
    def save_audio(self):
        if self.audio_data is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        
        if file_path:
            try:
                sf.write(file_path, self.audio_data, self.sample_rate)
                self.status_var.set(f"Saved to: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")
                
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    editor = MusicEditor()
    editor.run()