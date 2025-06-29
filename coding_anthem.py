import tkinter as tk
from tkinter import ttk
import pygame
import time
from PIL import Image, ImageTk
import os

class CodingAnthem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("While True, We Loop - A Coding Anthem")
        self.window.geometry("1200x800")
        self.window.configure(bg='#1E1E1E')
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Song lyrics with timing (seconds)
        self.lyrics = [
            (0, "🎵 While True, We Loop 🎵"),
            (4, "Woke up, hit the keys, time to start my grind"),
            (8, "Python on my screen, got the logic in my mind"),
            (12, "While true, we loop, never gonna stop"),
            (16, "Syntax so clean, let the functions drop"),
            # Pre-Chorus
            (20, "404? Nah, I never lose my way"),
            (24, "Debugging all night, till I see the light of day"),
            (28, "Java in my coffee, scripts running tight"),
            (32, "Frontend shining, yeah, the UI lookin' right"),
            # Chorus
            (36, "While true, we loop, never hit a break"),
            (40, "Code so smooth, like a perfect escape"),
            (44, "Stack overflow, but I know what to do"),
            (48, "Ctrl + Z when I mess up the view"),
            # Verse 2
            (52, "Commit that repo, push it to the cloud"),
            (56, "Tech meme dropping, got the devs feeling proud"),
            (60, "React to the haters like a JavaScript state"),
            (64, "Catch that exception, yeah, we never show the hate"),
            # Bridge
            (68, "Git pull up, let's merge that vibe"),
            (72, "Code reviews lit, yeah, the squad stay live"),
            (76, "While loop spinning, recursion so tight"),
            (80, "Dark mode on, hacking deep in the night"),
            # Chorus Repeat
            (84, "While true, we loop, never hit a break"),
            (88, "Code so smooth, like a perfect escape"),
            (92, "Stack overflow, but I know what to do"),
            (96, "Ctrl + Z when I mess up the view"),
            # Outro
            (100, 'Print("Success, we made it alright")'),
            (104, "Server online, yeah, we shining so bright"),
            (108, "From Python to Java, we keepin' it cool"),
            (112, "While true, we loop—yeah, that's the rule!")
        ]
        
        self.current_line = 0
        self.create_gui()
        self.load_audio()
        
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Lyrics.TLabel", 
                       font=('Courier', 24),
                       background='#1E1E1E',
                       foreground='#00FF00')
        
        # Lyrics display
        self.lyrics_label = ttk.Label(main_frame, 
                                    text="Press Play to Start",
                                    style="Lyrics.TLabel",
                                    wraplength=1000,
                                    justify='center')
        self.lyrics_label.pack(expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=20)
        
        ttk.Button(control_frame, text="Play",
                  command=self.play_song).pack(side='left', padx=10)
        ttk.Button(control_frame, text="Stop",
                  command=self.stop_song).pack(side='left', padx=10)
        
        # Volume control
        self.volume_var = tk.DoubleVar(value=0.7)
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(pady=10)
        
        ttk.Label(volume_frame, text="Volume:").pack(side='left')
        volume_slider = ttk.Scale(volume_frame,
                                from_=0, to=1,
                                orient='horizontal',
                                variable=self.volume_var,
                                command=self.update_volume)
        volume_slider.pack(side='left', padx=10)
        
        # Visual effects canvas
        self.canvas = tk.Canvas(main_frame, 
                              width=1000, height=200,
                              bg='#1E1E1E',
                              highlightthickness=0)
        self.canvas.pack(pady=20)
        
    def load_audio(self):
        try:
            pygame.mixer.music.load("assets/background_music.mp3")
            pygame.mixer.music.set_volume(self.volume_var.get())
        except:
            print("Background music file not found")
            
    def update_volume(self, _=None):
        pygame.mixer.music.set_volume(self.volume_var.get())
        
    def play_song(self):
        pygame.mixer.music.play()
        self.current_line = 0
        self.update_lyrics()
        self.animate_visuals()
        
    def stop_song(self):
        pygame.mixer.music.stop()
        self.lyrics_label.config(text="Press Play to Start")
        self.canvas.delete('all')
        
    def update_lyrics(self):
        if self.current_line < len(self.lyrics):
            timing, line = self.lyrics[self.current_line]
            self.lyrics_label.config(text=line)
            self.current_line += 1
            self.window.after(4000, self.update_lyrics)  # 4 seconds per line
            
    def animate_visuals(self):
        self.canvas.delete('all')
        
        # Create visual effects
        colors = ['#00FF00', '#00CC00', '#009900']
        for i in range(20):
            x = i * 50
            height = abs(int(100 * pygame.mixer.music.get_volume() * 
                           (1 + math.sin(time.time() * 5 + i))))
            self.canvas.create_rectangle(x, 200-height, x+30, 200,
                                      fill=random.choice(colors))
            
        if pygame.mixer.music.get_busy():
            self.window.after(50, self.animate_visuals)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    song = CodingAnthem()
    song.run()