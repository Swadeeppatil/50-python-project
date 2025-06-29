import tkinter as tk
from tkinter import ttk, messagebox
import instaloader
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import threading

class InstagramAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Profile Analyzer")
        self.root.geometry("1200x800")
        
        # Initialize Instagram loader
        self.L = instaloader.Instaloader()
        self.profile_data = None
        self.posts_data = []
        self.reels_data = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Input and Controls
        left_panel = ttk.Frame(self.main_container)
        self.main_container.add(left_panel)
        
        # Profile input
        input_frame = ttk.LabelFrame(left_panel, text="Profile Analysis", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Enter Instagram Profile URL:").pack()
        self.profile_url = ttk.Entry(input_frame, width=40)
        self.profile_url.pack(pady=5)
        
        self.analyze_btn = ttk.Button(input_frame, text="Analyze Profile", 
                                    command=self.start_analysis)
        self.analyze_btn.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(input_frame, mode='indeterminate')
        
        # Right panel - Results
        right_panel = ttk.Notebook(self.main_container)
        self.main_container.add(right_panel)
        
        # Profile Overview tab
        self.overview_frame = ttk.Frame(right_panel)
        right_panel.add(self.overview_frame, text="Profile Overview")
        
        # Stats tab
        self.stats_frame = ttk.Frame(right_panel)
        right_panel.add(self.stats_frame, text="Detailed Stats")
        
        # Recommendations tab
        self.recommendations_frame = ttk.Frame(right_panel)
        right_panel.add(self.recommendations_frame, text="Growth Recommendations")
        
    def start_analysis(self):
        profile_url = self.profile_url.get()
        if not profile_url:
            messagebox.showwarning("Warning", "Please enter an Instagram profile URL!")
            return
        
        try:
            username = self.extract_username(profile_url)
            self.analyze_btn.config(state='disabled')
            self.progress.pack(pady=5)
            self.progress.start()
            
            # Start analysis in separate thread
            threading.Thread(target=self.analyze_profile, 
                           args=(username,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid URL: {str(e)}")
            
    def extract_username(self, url):
        # Extract username from Instagram URL
        return url.split('instagram.com/')[-1].strip('/')
        
    def analyze_profile(self, username):
        try:
            # Load profile
            profile = instaloader.Profile.from_username(self.L.context, username)
            
            # Collect profile data
            self.profile_data = {
                'username': profile.username,
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'bio': profile.biography,
                'external_url': profile.external_url,
                'is_business': profile.is_business_account,
            }
            
            # Collect posts and reels data
            posts_data = []
            reels_data = []
            
            for post in profile.get_posts():
                if post.is_video:
                    reels_data.append({
                        'date': post.date,
                        'likes': post.likes,
                        'comments': post.comments,
                        'video_view_count': post.video_view_count,
                        'caption': post.caption,
                        'hashtags': post.caption_hashtags,
                    })
                else:
                    posts_data.append({
                        'date': post.date,
                        'likes': post.likes,
                        'comments': post.comments,
                        'caption': post.caption,
                        'hashtags': post.caption_hashtags,
                    })
                
                if len(posts_data) + len(reels_data) >= 30:  # Limit to recent 30 posts
                    break
            
            self.posts_data = posts_data
            self.reels_data = reels_data
            
            # Update UI
            self.root.after(0, self.update_ui)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                                                          f"Analysis failed: {str(e)}"))
        finally:
            self.root.after(0, self.cleanup_ui)
            
    def update_ui(self):
        # Clear previous results
        for widget in self.overview_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        for widget in self.recommendations_frame.winfo_children():
            widget.destroy()
            
        # Update Overview tab
        self.update_overview_tab()
        
        # Update Stats tab
        self.update_stats_tab()
        
        # Update Recommendations tab
        self.update_recommendations_tab()
        
    def update_overview_tab(self):
        # Profile summary
        summary_frame = ttk.LabelFrame(self.overview_frame, text="Profile Summary", 
                                     padding=10)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(summary_frame, 
                 text=f"Username: {self.profile_data['username']}").pack()
        ttk.Label(summary_frame, 
                 text=f"Followers: {self.profile_data['followers']:,}").pack()
        ttk.Label(summary_frame, 
                 text=f"Following: {self.profile_data['following']:,}").pack()
        ttk.Label(summary_frame, 
                 text=f"Posts: {self.profile_data['posts_count']:,}").pack()
        
    def update_stats_tab(self):
        if self.reels_data:
            # Reels performance
            reels_frame = ttk.LabelFrame(self.stats_frame, text="Reels Performance", 
                                       padding=10)
            reels_frame.pack(fill=tk.X, padx=5, pady=5)
            
            avg_views = np.mean([r['video_view_count'] for r in self.reels_data])
            max_views = max([r['video_view_count'] for r in self.reels_data])
            
            ttk.Label(reels_frame, 
                     text=f"Average Views: {int(avg_views):,}").pack()
            ttk.Label(reels_frame, 
                     text=f"Highest Views: {max_views:,}").pack()
            
        # Engagement rate
        engagement_frame = ttk.LabelFrame(self.stats_frame, text="Engagement Metrics", 
                                        padding=10)
        engagement_frame.pack(fill=tk.X, padx=5, pady=5)
        
        all_posts = self.posts_data + self.reels_data
        if all_posts:
            avg_likes = np.mean([p['likes'] for p in all_posts])
            avg_comments = np.mean([p['comments'] for p in all_posts])
            engagement_rate = ((avg_likes + avg_comments) / 
                             self.profile_data['followers']) * 100
            
            ttk.Label(engagement_frame, 
                     text=f"Average Likes: {int(avg_likes):,}").pack()
            ttk.Label(engagement_frame, 
                     text=f"Average Comments: {int(avg_comments):,}").pack()
            ttk.Label(engagement_frame, 
                     text=f"Engagement Rate: {engagement_rate:.2f}%").pack()
            
    def update_recommendations_tab(self):
        recommendations = self.generate_recommendations()
        
        for category, tips in recommendations.items():
            category_frame = ttk.LabelFrame(self.recommendations_frame, 
                                          text=category, padding=10)
            category_frame.pack(fill=tk.X, padx=5, pady=5)
            
            for tip in tips:
                ttk.Label(category_frame, text=f"• {tip}", wraplength=500).pack(pady=2)
                
    def generate_recommendations(self):
        recommendations = {
            "Content Strategy": [],
            "Engagement Improvement": [],
            "Profile Optimization": [],
        }
        
        # Analyze posting patterns
        if self.reels_data:
            avg_reel_views = np.mean([r['video_view_count'] for r in self.reels_data])
            if avg_reel_views < self.profile_data['followers'] * 0.3:
                recommendations["Content Strategy"].append(
                    "Your reels are getting lower views than potential. "
                    "Try posting when your audience is most active."
                )
        
        # Analyze engagement rate
        all_posts = self.posts_data + self.reels_data
        if all_posts:
            engagement_rate = ((np.mean([p['likes'] for p in all_posts]) + 
                              np.mean([p['comments'] for p in all_posts])) / 
                             self.profile_data['followers']) * 100
            
            if engagement_rate < 3:
                recommendations["Engagement Improvement"].append(
                    "Your engagement rate is below average. Try using more engaging "
                    "captions and call-to-actions in your posts."
                )
        
        # Analyze profile optimization
        if not self.profile_data['bio']:
            recommendations["Profile Optimization"].append(
                "Add a compelling bio to help potential followers understand "
                "your content focus."
            )
            
        if not self.profile_data['external_url'] and self.profile_data['is_business']:
            recommendations["Profile Optimization"].append(
                "Add a website link to your bio to drive traffic to your other platforms."
            )
            
        # Add general recommendations based on profile type
        if self.profile_data['is_business']:
            recommendations["Content Strategy"].append(
                "Consider creating more educational content related to your business "
                "niche to establish authority."
            )
            
        return recommendations
    
    def cleanup_ui(self):
        self.analyze_btn.config(state='normal')
        self.progress.stop()
        self.progress.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramAnalyzer(root)
    root.mainloop()