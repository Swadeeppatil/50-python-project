import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import git
import os
from datetime import datetime
import threading
import json

class GitHubClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("GitHub Desktop Clone")
        self.window.geometry("1200x800")
        self.window.configure(bg='#0D1117')
        
        self.current_repo = None
        self.load_config()
        self.create_gui()
        
    def load_config(self):
        self.config_file = 'github_config.json'
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'repositories': [],
                'github_username': '',
                'github_token': ''
            }
            
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
            
    def create_gui(self):
        # Main toolbar
        toolbar = tk.Frame(self.window, bg='#161B22')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Clone Repository",
                  command=self.clone_repository).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Local Repository",
                  command=self.add_local_repository).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Settings",
                  command=self.show_settings).pack(side=tk.RIGHT, padx=5)
        
        # Main content area
        content = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg='#0D1117')
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Repository list
        repo_frame = tk.Frame(content, bg='#161B22')
        content.add(repo_frame)
        
        tk.Label(repo_frame, text="Repositories", bg='#161B22',
                fg='white', font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.repo_list = ttk.Treeview(repo_frame, height=20,
                                    selectmode='browse', show='tree')
        self.repo_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.repo_list.bind('<<TreeviewSelect>>', self.on_repo_select)
        
        # Repository details
        details_frame = tk.Frame(content, bg='#161B22')
        content.add(details_frame)
        
        # Changes section
        changes_frame = tk.LabelFrame(details_frame, text="Changes",
                                    bg='#161B22', fg='white')
        changes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.changes_list = ttk.Treeview(changes_frame,
                                       columns=('Status',),
                                       show='tree headings')
        self.changes_list.heading('Status', text='Status')
        self.changes_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Commit section
        commit_frame = tk.Frame(details_frame, bg='#161B22')
        commit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(commit_frame, text="Commit Message:",
                bg='#161B22', fg='white').pack(pady=5)
        
        self.commit_msg = scrolledtext.ScrolledText(commit_frame, height=3,
                                                  bg='#0D1117', fg='white')
        self.commit_msg.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(commit_frame, text="Commit Changes",
                  command=self.commit_changes).pack(pady=5)
        
        # Push/Pull frame
        sync_frame = tk.Frame(details_frame, bg='#161B22')
        sync_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(sync_frame, text="Push",
                  command=self.push_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(sync_frame, text="Pull",
                  command=self.pull_changes).pack(side=tk.LEFT, padx=5)
        
        self.load_repositories()
        
    def clone_repository(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Clone Repository")
        dialog.geometry("400x200")
        dialog.configure(bg='#161B22')
        
        tk.Label(dialog, text="Repository URL:",
                bg='#161B22', fg='white').pack(pady=5)
        url_entry = ttk.Entry(dialog, width=50)
        url_entry.pack(pady=5)
        
        tk.Label(dialog, text="Local Path:",
                bg='#161B22', fg='white').pack(pady=5)
        path_entry = ttk.Entry(dialog, width=50)
        path_entry.pack(pady=5)
        
        def browse_path():
            path = filedialog.askdirectory()
            if path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, path)
                
        ttk.Button(dialog, text="Browse",
                  command=browse_path).pack(pady=5)
        
        def do_clone():
            url = url_entry.get()
            path = path_entry.get()
            try:
                git.Repo.clone_from(url, path)
                self.config['repositories'].append(path)
                self.save_config()
                self.load_repositories()
                dialog.destroy()
                messagebox.showinfo("Success", "Repository cloned successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clone: {str(e)}")
                
        ttk.Button(dialog, text="Clone",
                  command=do_clone).pack(pady=10)
        
    def add_local_repository(self):
        path = filedialog.askdirectory()
        if path:
            try:
                repo = git.Repo(path)
                if repo.git_dir:
                    self.config['repositories'].append(path)
                    self.save_config()
                    self.load_repositories()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid git repository: {str(e)}")
                
    def load_repositories(self):
        self.repo_list.delete(*self.repo_list.get_children())
        for path in self.config['repositories']:
            name = os.path.basename(path)
            self.repo_list.insert('', 'end', text=name, values=(path,))
            
    def on_repo_select(self, event):
        selection = self.repo_list.selection()
        if selection:
            path = self.repo_list.item(selection[0])['values'][0]
            self.current_repo = git.Repo(path)
            self.refresh_changes()
            
    def refresh_changes(self):
        if not self.current_repo:
            return
            
        self.changes_list.delete(*self.changes_list.get_children())
        
        # Untracked files
        for file in self.current_repo.untracked_files:
            self.changes_list.insert('', 'end', text=file, values=('Untracked',))
            
        # Modified files
        diff = self.current_repo.index.diff(None)
        for d in diff:
            self.changes_list.insert('', 'end', text=d.a_path, values=('Modified',))
            
    def commit_changes(self):
        if not self.current_repo:
            return
            
        message = self.commit_msg.get('1.0', tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a commit message")
            return
            
        try:
            self.current_repo.git.add('.')
            self.current_repo.index.commit(message)
            self.refresh_changes()
            self.commit_msg.delete('1.0', tk.END)
            messagebox.showinfo("Success", "Changes committed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to commit: {str(e)}")
            
    def push_changes(self):
        if not self.current_repo:
            return
            
        try:
            origin = self.current_repo.remote('origin')
            origin.push()
            messagebox.showinfo("Success", "Changes pushed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to push: {str(e)}")
            
    def pull_changes(self):
        if not self.current_repo:
            return
            
        try:
            origin = self.current_repo.remote('origin')
            origin.pull()
            self.refresh_changes()
            messagebox.showinfo("Success", "Changes pulled successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pull: {str(e)}")
            
    def show_settings(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Settings")
        dialog.geometry("400x200")
        dialog.configure(bg='#161B22')
        
        tk.Label(dialog, text="GitHub Username:",
                bg='#161B22', fg='white').pack(pady=5)
        username = ttk.Entry(dialog, width=40)
        username.insert(0, self.config.get('github_username', ''))
        username.pack(pady=5)
        
        tk.Label(dialog, text="GitHub Token:",
                bg='#161B22', fg='white').pack(pady=5)
        token = ttk.Entry(dialog, width=40, show='*')
        token.insert(0, self.config.get('github_token', ''))
        token.pack(pady=5)
        
        def save_settings():
            self.config['github_username'] = username.get()
            self.config['github_token'] = token.get()
            self.save_config()
            dialog.destroy()
            
        ttk.Button(dialog, text="Save",
                  command=save_settings).pack(pady=10)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = GitHubClient()
    app.run()