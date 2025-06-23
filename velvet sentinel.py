import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sys
import subprocess

class VelvetSentinel:
    def __init__(self, root):
        self.root = root
        self.root.title("Velvet Sentinel")
        self.root.geometry("650x500")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(".", background="#0a0a0a", foreground="#e6e6e6")
        self.style.configure("TFrame", background="#0a0a0a")
        self.style.configure("TLabel", background="#0a0a0a", foreground="#e6e6e6", font=("Helvetica", 10))
        self.style.configure("TButton", background="#2a1e30", foreground="#e6e6e6", font=("Helvetica", 10), borderwidth=0)
        self.style.map("TButton", background=[("active", "#3d2a45")])
        self.style.configure("TEntry", fieldbackground="#1a1a1a", foreground="#e6e6e6")
        self.style.configure("Treeview", background="#1a1a1a", fieldbackground="#1a1a1a", foreground="#e6e6e6", rowheight=25)
        self.style.map("Treeview", background=[("selected", "#3d2a45")])

        self.main_container = ttk.Frame(root, padding=(30, 20))
        self.main_container.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(pady=(0, 20))
        ttk.Label(header_frame, text="VELVET SENTINEL", font=("Helvetica", 20, "bold"), foreground="#b28cce").pack()
        ttk.Label(header_frame, text="LUXURY FILE MONITORING SERVICE", font=("Helvetica", 10), foreground="#b28cce").pack(pady=(5, 0))

        folder_frame = ttk.Frame(self.main_container)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(folder_frame, text="MONITORED FOLDER:", font=("Helvetica", 9)).pack(anchor=tk.W)
        self.folder_entry = ttk.Entry(folder_frame, font=("Helvetica", 10), width=50)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="BROWSE", command=self.select_folder, width=8).pack(side=tk.RIGHT)

        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        self.start_btn = ttk.Button(control_frame, text="START MONITORING", command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_btn = ttk.Button(control_frame, text="STOP", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        ttk.Button(control_frame, text="CLEAR LOG", command=self.clear_log).pack(side=tk.RIGHT)

        log_frame = ttk.Frame(self.main_container)
        log_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("time", "event", "file")
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings", selectmode="extended", height=12)
        self.log_tree.heading("time", text="TIME", anchor=tk.W)
        self.log_tree.heading("event", text="EVENT", anchor=tk.W)
        self.log_tree.heading("file", text="FILE", anchor=tk.W)
        self.log_tree.column("time", width=120, stretch=tk.NO)
        self.log_tree.column("event", width=100, stretch=tk.NO)
        self.log_tree.column("file", width=380, stretch=tk.YES)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_container, text="FOR THE DISCREET PROFESSIONAL", font=("Helvetica", 8), foreground="#555555").pack(side=tk.BOTTOM, pady=(10, 0))

        self.tracking = False
        self.folder_path = ""
        self.before_state = {}

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.before_state = self.get_folder_state()

    def get_folder_state(self):
        state = {}
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                path = os.path.join(root, file)
                state[path] = os.path.getmtime(path)
        return state

    def start_monitoring(self):
        if not self.folder_path:
            messagebox.showwarning("Warning", "Please select a folder first")
            return
            
        self.tracking = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.before_state = self.get_folder_state()
        self.monitor_changes()

    def stop_monitoring(self):
        self.tracking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def monitor_changes(self):
        if not self.tracking:
            return
            
        current_state = self.get_folder_state()
        
        for path in set(self.before_state) - set(current_state):
            self.log_event("DELETED", os.path.relpath(path, self.folder_path))
        
        for path in current_state:
            if path not in self.before_state:
                self.log_event("CREATED", os.path.relpath(path, self.folder_path))
            elif current_state[path] != self.before_state[path]:
                self.log_event("MODIFIED", os.path.relpath(path, self.folder_path))
        
        self.before_state = current_state
        self.root.after(1000, self.monitor_changes)

    def log_event(self, event, filename):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_tree.insert("", tk.END, values=(timestamp, event, filename))
        self.log_tree.yview_moveto(1)

    def clear_log(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = VelvetSentinel(root)
    root.mainloop()