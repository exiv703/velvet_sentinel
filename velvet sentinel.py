import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
from datetime import datetime
import tempfile
from collections import defaultdict
import win10toast
import json
import send2trash
import platform
import glob
import customtkinter as ctk
import threading
import time
import subprocess
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class VelvetSentinelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Velvet Sentinel - NextGen")
        self.geometry("1200x800")
        self.resizable(False, False)
        self.configure(bg="#101820")
        self.settings = {
            "notifications": False,
            "notify_created": True,
            "notify_modified": True,
            "notify_deleted": True,
            "duration": 3,
            "sound": False,
            "use_system_trash": True,
            "debug_mode": False,
            "auto_backup": False,
            "backup_interval": 24
        }
        self.load_settings()
        self.monitored_folders = set()
        self.before_states = defaultdict(dict)
        self.deleted_files = {}
        self.trash_dir = os.path.join(tempfile.gettempdir(), "VelvetTrash")
        self.metadata_file = os.path.join(self.trash_dir, "metadata.json")
        os.makedirs(self.trash_dir, exist_ok=True)
        self.load_deleted_files_metadata()
        self.tracking = False
        self.debug_mode = self.settings.get("debug_mode", False)
        self.check_and_repair_metadata()
        self.create_layout()
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#181f2a",
                        fieldbackground="#181f2a",
                        foreground="#e6e6e6",
                        bordercolor="#232b3a",
                        borderwidth=0,
                        font=("Consolas", 12))
        style.configure("Treeview.Heading",
                        background="#232b3a",
                        foreground="#7fffd4",
                        font=("Arial", 12, "bold"))
        style.map("Treeview",
                  background=[('selected', '#2e3b4e')])
    def create_layout(self):
        self.notebook = ctk.CTkTabview(self, fg_color="#181f2a", segmented_button_fg_color="#232b3a")
        self.notebook.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        main_tab = self.notebook.add("Main")
        self.create_main_tab(main_tab)
        monitor_tab = self.notebook.add("Monitoring")
        self.create_monitor_tab(monitor_tab)
        trash_tab = self.notebook.add("Trash")
        self.create_trash_tab(trash_tab)
        settings_tab = self.notebook.add("Settings")
        self.create_settings_tab(settings_tab)
        backup_tab = self.notebook.add("Backup")
        self.create_backup_tab(backup_tab)

    def create_main_tab(self, parent):
        header = ctk.CTkFrame(parent, fg_color="#1e2a38", corner_radius=16, height=120)
        header.pack(fill=ctk.X, pady=(0, 20))
        header.grid_propagate(False)
        icon = ctk.CTkLabel(header, text="🛡️", font=("Arial", 48))
        icon.grid(row=0, column=0, rowspan=2, padx=30, pady=20)
        self.status_label = ctk.CTkLabel(header, text="Computer is protected", font=("Arial", 28, "bold"), text_color="#7fffd4")
        self.status_label.grid(row=0, column=1, sticky="w", pady=(30, 0))
        subtitle = ctk.CTkLabel(header, text="Velvet Sentinel - Multi-Folder Monitoring & Recovery", font=("Arial", 14), text_color="#b2c2d6")
        subtitle.grid(row=1, column=1, sticky="w", pady=(0, 20))
        header.columnconfigure(1, weight=1)

        button_frame = ctk.CTkFrame(parent, fg_color="#181f2a")
        button_frame.pack(fill=ctk.X, pady=(0, 20))
        ctk.CTkButton(button_frame, text="🟢  Start monitoring", command=self.start_monitoring, width=160, height=48, font=("Arial", 16), corner_radius=12).grid(row=0, column=0, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="⏹️  Stop monitoring", command=self.stop_monitoring, width=160, height=48, font=("Arial", 16), corner_radius=12).grid(row=0, column=1, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="🔍  Scan", command=self.scan_for_deleted_files, width=160, height=48, font=("Arial", 16), corner_radius=12).grid(row=0, column=2, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="💾  Backup", command=self.create_backup_system, width=160, height=48, font=("Arial", 16), corner_radius=12).grid(row=0, column=3, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="📄  Export logs", command=self.export_logs, width=160, height=48, font=("Arial", 16), corner_radius=12).grid(row=0, column=4, padx=18, pady=10)
        button_frame.columnconfigure(tuple(range(5)), weight=1)

        log_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        log_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))
        ctk.CTkLabel(log_frame, text="Event log:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.log_text = ctk.CTkTextbox(log_frame, font=("Consolas", 12), width=900, height=300, fg_color="#181f2a", text_color="#e6e6e6")
        self.log_text.pack(fill=ctk.BOTH, expand=True, padx=18, pady=10)
        self.log_text.insert("end", "Program started...\n")
        self.log_text.configure(state="disabled")

    def create_monitor_tab(self, parent):
        folder_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        folder_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkLabel(folder_frame, text="Monitored folders:", font=("Arial", 14, "bold"), text_color="#7fffd4").grid(row=0, column=0, padx=18, pady=10, sticky="w")
        self.folder_listbox = ctk.CTkComboBox(folder_frame, values=list(self.monitored_folders), width=400, font=("Arial", 12))
        self.folder_listbox.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(folder_frame, text="Add", command=self.add_folder, width=80).grid(row=0, column=2, padx=8)
        ctk.CTkButton(folder_frame, text="Remove", command=self.remove_folder, width=80).grid(row=0, column=3, padx=8)
        folder_frame.columnconfigure(1, weight=1)

        list_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        list_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))
        ctk.CTkLabel(list_frame, text="List of monitored folders:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.folder_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="#181f2a", height=200)
        self.folder_scroll.pack(fill=ctk.BOTH, expand=True, padx=18, pady=10)
        self.update_folder_display()

    def create_trash_tab(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        button_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkButton(button_frame, text="♻️  Restore selected", command=self.restore_selected, width=150, height=40, font=("Arial", 14)).grid(row=0, column=0, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="🗑️  Clean trash", command=self.clean_trash, width=150, height=40, font=("Arial", 14)).grid(row=0, column=1, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="📂  Open trash folder", command=self.open_trash_folder, width=150, height=40, font=("Arial", 14)).grid(row=0, column=2, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="🔧  Check and repair metadata", command=self.check_and_repair_metadata, width=150, height=40, font=("Arial", 14)).grid(row=0, column=3, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="🔄  Refresh", command=self.refresh_trash_display, width=150, height=40, font=("Arial", 14)).grid(row=0, column=4, padx=18, pady=10)
        button_frame.columnconfigure(tuple(range(5)), weight=1)

        list_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        list_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))
        ctk.CTkLabel(list_frame, text="Deleted files:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        tree_frame = ctk.CTkFrame(list_frame, fg_color="#181f2a")
        tree_frame.pack(fill=ctk.BOTH, expand=True, padx=18, pady=10)
        self.trash_tree = ttk.Treeview(tree_frame, columns=("Deletion time", "Original folder", "Status"), show="tree headings", height=15)
        self.trash_tree.heading("#0", text="File name")
        self.trash_tree.heading("Deletion time", text="Deletion time")
        self.trash_tree.heading("Original folder", text="Original folder")
        self.trash_tree.heading("Status", text="Status")
        self.trash_tree.column("#0", width=300)
        self.trash_tree.column("Deletion time", width=150)
        self.trash_tree.column("Original folder", width=200)
        self.trash_tree.column("Status", width=100)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.trash_tree.yview)
        self.trash_tree.configure(yscrollcommand=scrollbar.set)
        self.trash_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.update_trash_display()

    def create_settings_tab(self, parent):
        notif_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        notif_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkLabel(notif_frame, text="Notifications:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.notif_switch = ctk.CTkSwitch(notif_frame, text="Enable notifications", command=self.toggle_notifications)
        self.notif_switch.pack(anchor="w", padx=18, pady=5)
        self.notif_switch.select() if self.settings["notifications"] else self.notif_switch.deselect()
        self.notif_created = ctk.CTkSwitch(notif_frame, text="Notify on new files", command=self.toggle_notify_created)
        self.notif_created.pack(anchor="w", padx=18, pady=5)
        self.notif_created.select() if self.settings["notify_created"] else self.notif_created.deselect()
        self.notif_modified = ctk.CTkSwitch(notif_frame, text="Notify on modifications", command=self.toggle_notify_modified)
        self.notif_modified.pack(anchor="w", padx=18, pady=5)
        self.notif_modified.select() if self.settings["notify_modified"] else self.notif_modified.deselect()
        self.notif_deleted = ctk.CTkSwitch(notif_frame, text="Notify on deletions", command=self.toggle_notify_deleted)
        self.notif_deleted.pack(anchor="w", padx=18, pady=5)
        self.notif_deleted.select() if self.settings["notify_deleted"] else self.notif_deleted.deselect()
        trash_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        trash_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkLabel(trash_frame, text="Trash:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.system_trash_switch = ctk.CTkSwitch(trash_frame, text="Use system trash", command=self.toggle_system_trash)
        self.system_trash_switch.pack(anchor="w", padx=18, pady=5)
        self.system_trash_switch.select() if self.settings["use_system_trash"] else self.system_trash_switch.deselect()
        debug_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        debug_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkLabel(debug_frame, text="Debug:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.debug_switch = ctk.CTkSwitch(debug_frame, text="Debug mode", command=self.toggle_debug_mode)
        self.debug_switch.pack(anchor="w", padx=18, pady=5)
        self.debug_switch.select() if self.settings["debug_mode"] else self.debug_switch.deselect()
        ctk.CTkButton(parent, text="💾 Save settings", command=self.save_settings, width=200, height=40, font=("Arial", 14)).pack(pady=20)

    def create_backup_tab(self, parent):
        backup_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        backup_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkLabel(backup_frame, text="Automatic backup:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.auto_backup_switch = ctk.CTkSwitch(backup_frame, text="Enable automatic backup", command=self.toggle_auto_backup)
        self.auto_backup_switch.pack(anchor="w", padx=18, pady=5)
        self.auto_backup_switch.select() if self.settings["auto_backup"] else self.auto_backup_switch.deselect()
        interval_frame = ctk.CTkFrame(backup_frame, fg_color="#181f2a")
        interval_frame.pack(fill=ctk.X, padx=18, pady=10)
        ctk.CTkLabel(interval_frame, text="Backup interval (hours):", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        self.backup_interval = ctk.CTkEntry(interval_frame, width=100)
        self.backup_interval.pack(side="right", padx=10, pady=10)
        self.backup_interval.insert(0, str(self.settings.get("backup_interval", 24)))
        button_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        button_frame.pack(fill=ctk.X, pady=(0, 18))
        ctk.CTkButton(button_frame, text="💾 Create backup", command=self.create_backup_system, width=200, height=40, font=("Arial", 14)).grid(row=0, column=0, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="📂 Select backup folder", command=self.select_backup_folder, width=200, height=40, font=("Arial", 14)).grid(row=0, column=1, padx=18, pady=10)
        ctk.CTkButton(button_frame, text="🔄 Restore from backup", command=self.restore_from_backup, width=200, height=40, font=("Arial", 14)).grid(row=0, column=2, padx=18, pady=10)
        button_frame.columnconfigure(tuple(range(3)), weight=1)
        list_frame = ctk.CTkFrame(parent, fg_color="#232b3a", corner_radius=14)
        list_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))
        ctk.CTkLabel(list_frame, text="Available backups:", font=("Arial", 14, "bold"), text_color="#7fffd4").pack(anchor="w", padx=18, pady=(10, 0))
        self.backup_listbox = ctk.CTkTextbox(list_frame, font=("Consolas", 12), height=200, fg_color="#181f2a", text_color="#e6e6e6")
        self.backup_listbox.pack(fill=ctk.BOTH, expand=True, padx=18, pady=10)
        self.update_backup_list()

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.monitored_folders:
            self.monitored_folders.add(folder)
            self.update_folder_listbox()
            self.update_folder_display()
            self.log_event(f"Added folder: {folder}")

    def remove_folder(self):
        folder = self.folder_listbox.get()
        if folder and folder in self.monitored_folders:
            self.monitored_folders.remove(folder)
            self.update_folder_listbox()
            self.update_folder_display()
            self.log_event(f"Removed folder: {folder}")

    def update_folder_listbox(self):
        self.folder_listbox.configure(values=list(self.monitored_folders))
        if self.monitored_folders:
            self.folder_listbox.set(next(iter(self.monitored_folders)))
        else:
            self.folder_listbox.set("")

    def update_folder_display(self):
        for widget in self.folder_scroll.winfo_children():
            widget.destroy()
        for folder in self.monitored_folders:
            folder_frame = ctk.CTkFrame(self.folder_scroll, fg_color="#232b3a")
            folder_frame.pack(fill=ctk.X, padx=5, pady=2)
            ctk.CTkLabel(folder_frame, text=folder, font=("Arial", 12)).pack(side="left", padx=10, pady=5)
            ctk.CTkButton(folder_frame, text="Remove", command=lambda f=folder: self.remove_specific_folder(f), width=60).pack(side="right", padx=5, pady=5)

    def remove_specific_folder(self, folder):
        if folder in self.monitored_folders:
            self.monitored_folders.remove(folder)
            self.update_folder_listbox()
            self.update_folder_display()
            self.log_event(f"Removed folder: {folder}")

    def start_monitoring(self):
        if not self.monitored_folders:
            messagebox.showwarning("Warning", "First add folders to monitor!")
            return
        self.tracking = True
        self.status_label.configure(text="Monitoring active", text_color="#7fffd4")
        for folder in self.monitored_folders:
            self.before_states[folder] = self.get_folder_state(folder)
        self.monitor_changes()
        self.log_event("Monitoring started.")

    def stop_monitoring(self):
        self.tracking = False
        self.status_label.configure(text="Monitoring stopped", text_color="#b2c2d6")
        self.log_event("Monitoring stopped.")

    def monitor_changes(self):
        if not self.tracking:
            return
        for folder in list(self.monitored_folders):
            try:
                if not os.path.exists(folder):
                    self.log_event(f"Folder does not exist: {folder}")
                    continue
                current_state = self.get_folder_state(folder)
                before_state = self.before_states[folder]
                deleted_files = set(before_state) - set(current_state)
                for path in deleted_files:
                    path = os.path.normpath(path)
                    if os.path.exists(path):
                        continue
                    relative_path = os.path.relpath(path, folder)
                    self.log_event(f"DELETED: {relative_path} ({path})")
                    if not self.settings["use_system_trash"]:
                        trash_path = self.move_to_trash(path)
                        if trash_path:
                            normalized_path = os.path.normpath(path)
                            self.deleted_files[normalized_path] = {
                                'deletion_time': datetime.now().isoformat(),
                                'original_folder': folder,
                                'trash_path': trash_path
                            }
                            self.save_deleted_files_metadata()
                            self.log_event(f"Saved metadata for: {normalized_path}")
                for path in current_state:
                    path = os.path.normpath(path)
                    if path not in before_state:
                        relative_path = os.path.relpath(path, folder)
                        self.log_event(f"ADDED: {relative_path} ({path})")
                    elif (current_state[path]['mtime'] != before_state[path]['mtime'] or 
                          current_state[path]['size'] != before_state[path]['size']):
                        relative_path = os.path.relpath(path, folder)
                        self.log_event(f"MODIFIED: {relative_path} ({path})")
                self.before_states[folder] = current_state
            except Exception as e:
                self.log_event(f"Error monitoring folder {folder}: {e}")
        self.after(1000, self.monitor_changes)

    def get_folder_state(self, folder):
        state = {}
        try:
            for root, _, files in os.walk(folder):
                for file in files:
                    path = os.path.normpath(os.path.join(root, file))
                    try:
                        state[path] = {
                            'mtime': os.path.getmtime(path),
                            'size': os.path.getsize(path)
                        }
                    except OSError:
                        pass
        except Exception as e:
            self.log_event(f"Error accessing folder {folder}: {e}")
        return state

    def move_to_trash(self, filepath):
        try:
            filepath = os.path.normpath(filepath)
            self.log_event(f"Attempting to move to trash: {filepath}")
            if not os.path.exists(filepath):
                self.log_event(f"File does not exist (already deleted): {filepath}")
                return None
            if self.settings["use_system_trash"]:
                self.log_event(f"Using system trash for: {filepath}")
                send2trash.send2trash(filepath)
                return filepath
            else:
                self.log_event(f"Using custom trash for: {filepath}")
                filename = os.path.basename(filepath)
                trash_path = os.path.join(self.trash_dir, filename)
                counter = 1
                while os.path.exists(trash_path):
                    name, ext = os.path.splitext(filename)
                    trash_path = os.path.join(self.trash_dir, f"{name}_{counter}{ext}")
                    counter += 1
                if not os.path.exists(filepath):
                    self.log_event(f"File was deleted before moving: {filepath}")
                    return None
                shutil.move(filepath, trash_path)
                self.log_event(f"Successfully moved to trash: {filepath} -> {trash_path}")
                return trash_path
        except FileNotFoundError:
            self.log_event(f"File not found: {filepath}")
            return None
        except PermissionError:
            self.log_event(f"Missing permissions to move: {filepath}")
            return None
        except Exception as e:
            self.log_event(f"Error moving to trash: {e} for {filepath}")
            return None

    def restore_selected(self):
        selected_item = self.trash_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a file to restore!")
            return
        restored_count = 0
        for item in selected_item:
            file_name = self.trash_tree.item(item)['text']
            for original_path, metadata in list(self.deleted_files.items()):
                if os.path.basename(original_path) == file_name:
                    trash_path = metadata.get('trash_path')
                    if trash_path and os.path.exists(trash_path):
                        try:
                            os.makedirs(os.path.dirname(original_path), exist_ok=True)
                            restored_path = original_path
                            counter = 1
                            while os.path.exists(restored_path):
                                name, ext = os.path.splitext(original_path)
                                restored_path = f"{name}_restored_{counter}{ext}"
                                counter += 1
                            shutil.move(trash_path, restored_path)
                            self.log_event(f"RESTORED: {restored_path}")
                            del self.deleted_files[original_path]
                            self.save_deleted_files_metadata()
                            self.update_trash_display()
                            restored_count += 1
                        except Exception as e:
                            self.log_event(f"Error restoring {original_path}: {e}")
        if restored_count > 0:
            messagebox.showinfo("Restoration", f"Restored {restored_count} file(s)")
        else:
            messagebox.showinfo("Restoration", "No files to restore.")

    def clean_trash(self):
        try:
            for filename in os.listdir(self.trash_dir):
                file_path = os.path.join(self.trash_dir, filename)
                if file_path == self.metadata_file:
                    continue
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            self.deleted_files.clear()
            self.save_deleted_files_metadata()
            self.update_trash_display()
            self.log_event("Trash cleaned.")
            messagebox.showinfo("Trash", "Trash cleaned.")
        except Exception as e:
            self.log_event(f"Error cleaning trash: {e}")

    def open_trash_folder(self):
        try:
            if platform.system() == "Windows":
                os.startfile(self.trash_dir)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.trash_dir])
            else:
                subprocess.run(["xdg-open", self.trash_dir])
        except Exception as e:
            self.log_event(f"Error opening trash: {e}")

    def update_trash_display(self):
        for item in self.trash_tree.get_children():
            self.trash_tree.delete(item)
        for original_path, metadata in self.deleted_files.items():
            file_name = os.path.basename(original_path)
            deletion_time = metadata.get('deletion_time', '')
            original_folder = metadata.get('original_folder', '')
            trash_path = metadata.get('trash_path', '')
            status = "Available" if (trash_path and os.path.exists(trash_path)) else "Unknown"
            try:
                dt = datetime.fromisoformat(deletion_time)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = deletion_time
            self.trash_tree.insert("", "end", text=file_name, values=(formatted_time, original_folder, status))

    def scan_for_deleted_files(self):
        if not self.monitored_folders:
            messagebox.showwarning("Warning", "First add folders to monitor!")
            return
        self.log_event("Started scanning for deleted files...")
        def scan_thread():
            found_files = []
            for folder in self.monitored_folders:
                try:
                    current_state = self.get_folder_state(folder)
                    before_state = self.before_states.get(folder, {})
                    for path in set(before_state) - set(current_state):
                        path = os.path.normpath(path)
                        if not os.path.exists(path):
                            relative_path = os.path.relpath(path, folder)
                            found_files.append((relative_path, path, folder))
                except Exception as e:
                    self.log_event(f"Error scanning folder {folder}: {e}")
            if found_files:
                result_text = f"Found {len(found_files)} deleted files:\n\n"
                for relative_path, full_path, folder in found_files:
                    result_text += f"• {relative_path}\n  ({full_path})\n  Folder: {folder}\n\n"
                self.log_event(f"Scan completed. Found {len(found_files)} deleted files.")
                messagebox.showinfo("Scan Results", result_text)
            else:
                self.log_event("Scan completed. No deleted files found.")
                messagebox.showinfo("Scan Results", "No deleted files found.")
        
        threading.Thread(target=scan_thread, daemon=True).start()

    def create_backup_system(self):
        if not self.monitored_folders:
            messagebox.showwarning("Warning", "First add folders to monitor!")
            return
        
        backup_folder = filedialog.askdirectory(title="Select backup location")
        if not backup_folder:
            return
        
        def backup_thread():
            try:
                backup_dir = os.path.join(backup_folder, "VelvetBackup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
                os.makedirs(backup_dir, exist_ok=True)
                
                for folder in self.monitored_folders:
                    try:
                        folder_name = os.path.basename(folder)
                        target_folder = os.path.join(backup_dir, folder_name)
                        shutil.copytree(folder, target_folder, dirs_exist_ok=True)
                        self.log_event(f"Backup: {folder} -> {target_folder}")
                    except Exception as e:
                        self.log_event(f"Error backing up {folder}: {e}")
                
                self.log_event(f"Backup completed: {backup_dir}")
                messagebox.showinfo("Backup", f"Backup completed: {backup_dir}")
                self.update_backup_list()
            except Exception as e:
                self.log_event(f"Error creating backup: {e}")
                messagebox.showerror("Error", f"Error creating backup: {e}")
        
        threading.Thread(target=backup_thread, daemon=True).start()

    def select_backup_folder(self):
        folder = filedialog.askdirectory(title="Select backup folder")
        if folder:
            self.backup_folder = folder
            self.update_backup_list()
            self.log_event(f"Set backup folder: {folder}")

    def restore_from_backup(self):
        messagebox.showinfo("Info", "Backup restore function - to be implemented")

    def update_backup_list(self):
        self.backup_listbox.configure(state="normal")
        self.backup_listbox.delete("1.0", "end")
        backup_folder = getattr(self, 'backup_folder', None)
        if not backup_folder:
            self.backup_listbox.insert("end", "No backup folder selected.\nUse 'Select backup folder' to set location.")
        else:
            try:
                backups = []
                for item in os.listdir(backup_folder):
                    if item.startswith("VelvetBackup_"):
                        backup_path = os.path.join(backup_folder, item)
                        if os.path.isdir(backup_path):
                            backups.append((item, os.path.getmtime(backup_path)))
                backups.sort(key=lambda x: x[1], reverse=True)
                if backups:
                    self.backup_listbox.insert("end", f"Found {len(backups)} backups:\n\n")
                    for backup_name, mtime in backups:
                        dt = datetime.fromtimestamp(mtime)
                        self.backup_listbox.insert("end", f"• {backup_name}\n  Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                else:
                    self.backup_listbox.insert("end", "No backups found in selected folder.")
            except Exception as e:
                self.backup_listbox.insert("end", f"Error reading backups: {e}")
        self.backup_listbox.configure(state="disabled")

    def toggle_notifications(self):
        self.settings["notifications"] = self.notif_switch.get()

    def toggle_notify_created(self):
        self.settings["notify_created"] = self.notif_created.get()

    def toggle_notify_modified(self):
        self.settings["notify_modified"] = self.notif_modified.get()

    def toggle_notify_deleted(self):
        self.settings["notify_deleted"] = self.notif_deleted.get()

    def toggle_system_trash(self):
        self.settings["use_system_trash"] = self.system_trash_switch.get()

    def toggle_debug_mode(self):
        self.settings["debug_mode"] = self.debug_switch.get()
        self.debug_mode = self.settings["debug_mode"]

    def toggle_auto_backup(self):
        self.settings["auto_backup"] = self.auto_backup_switch.get()

    def save_settings(self):
        try:
            self.settings["backup_interval"] = int(self.backup_interval.get())
        except ValueError:
            self.settings["backup_interval"] = 24
        with open("velvet_settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
        self.log_event("Settings saved.")
        messagebox.showinfo("Settings", "Settings saved.")

    def show_notification(self, message):
        if self.settings["notifications"]:
            try:
                if platform.system() == "Windows":
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast("Velvet Sentinel", message, duration=self.settings["duration"])
                else:
                    messagebox.showinfo("Velvet Sentinel", message)
            except Exception as e:
                self.log_event(f"Error showing notification: {e}")

    def log_event(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} | {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def load_settings(self):
        try:
            if os.path.exists("velvet_settings.json"):
                with open("velvet_settings.json", "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
        except Exception:
            pass

    def load_deleted_files_metadata(self):
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.deleted_files = json.load(f)
        except Exception:
            self.deleted_files = {}

    def save_deleted_files_metadata(self):
        try:
            os.makedirs(self.trash_dir, exist_ok=True)
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.deleted_files, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def check_and_repair_metadata(self):
        try:
            repaired_count = 0
            for original_path, metadata in list(self.deleted_files.items()):
                trash_path = metadata.get('trash_path')
                if trash_path and not os.path.exists(trash_path):
                    self.log_event(f"Repairing metadata - file in trash does not exist: {trash_path}")
                    del self.deleted_files[original_path]
                    repaired_count += 1
            if repaired_count > 0:
                self.save_deleted_files_metadata()
                self.log_event(f"Repaired {repaired_count} metadata entries")
        except Exception as e:
            self.log_event(f"Error repairing metadata: {e}")

    def export_logs(self):
        try:
            filename = f"velvet_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            if not filepath:
                return
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("VELVET SENTINEL - LOG REPORT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Version: NextGen\n\n")
                f.write("STATISTICS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Monitored folders: {len(self.monitored_folders)}\n")
                f.write(f"Files in trash: {len(self.deleted_files)}\n")
                f.write(f"Monitoring active: {'Yes' if self.tracking else 'No'}\n")
                f.write(f"Uses system trash: {'Yes' if self.settings['use_system_trash'] else 'No'}\n\n")
                f.write("MONITORED FOLDERS:\n")
                f.write("-" * 30 + "\n")
                for folder in self.monitored_folders:
                    f.write(f"• {folder}\n")
                f.write("\n")
                f.write("FILES IN TRASH:\n")
                f.write("-" * 30 + "\n")
                for original_path, metadata in self.deleted_files.items():
                    f.write(f"• {os.path.basename(original_path)}\n")
                    f.write(f"  Original path: {original_path}\n")
                    f.write(f"  Folder: {metadata.get('original_folder', 'Unknown')}\n")
                    f.write(f"  Deletion time: {metadata.get('deletion_time', 'Unknown')}\n")
                    f.write(f"  Status: {'Available' if (metadata.get('trash_path') and os.path.exists(metadata.get('trash_path'))) else 'Unknown'}\n\n")
                f.write("EVENT LOG:\n")
                f.write("-" * 30 + "\n")
                log_content = self.log_text.get("1.0", "end")
                f.write(log_content)
            self.log_event(f"Logs exported to: {filepath}")
            messagebox.showinfo("Export", f"Logs exported to:\n{filepath}")
        except Exception as e:
            self.log_event(f"Error exporting logs: {e}")
            messagebox.showerror("Error", f"Error exporting logs: {e}")

    def refresh_trash_display(self):
        try:
            self.update_trash_display()
            self.log_event("Trash file list refreshed.")
        except Exception as e:
            self.log_event(f"Error refreshing trash list: {e}")

if __name__ == "__main__":
    app = VelvetSentinelApp()
    app.mainloop()
