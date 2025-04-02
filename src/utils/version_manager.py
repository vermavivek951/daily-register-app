import os
import json
import requests
from semantic_version import Version
import tkinter as tk
from tkinter import messagebox
import sys
import subprocess
import platform

class VersionManager:
    def __init__(self, current_version, update_url):
        self.current_version = Version(current_version)
        self.update_url = update_url
        self.version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'version.json')
        
    def check_for_updates(self):
        """Check if a new version is available"""
        try:
            response = requests.get(self.update_url)
            if response.status_code == 200:
                latest_version = Version(response.json()['version'])
                return latest_version > self.current_version, latest_version
            return False, None
        except Exception as e:
            print(f"Error checking for updates: {str(e)}")
            return False, None
            
    def show_update_dialog(self, latest_version):
        """Show a user-friendly update dialog"""
        dialog = tk.Tk()
        dialog.title("Software Update Available")
        dialog.geometry("400x200")
        dialog.configure(bg='#f0f0f0')
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make dialog modal
        dialog.transient(dialog.master)
        dialog.grab_set()
        
        # Add message
        message = f"A new version ({latest_version}) is available!\n\n"
        message += "Would you like to update now?\n"
        message += "Your data will be preserved."
        
        tk.Label(
            dialog,
            text=message,
            bg='#f0f0f0',
            font=('Segoe UI', 10),
            pady=20
        ).pack()
        
        # Add buttons
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        def update():
            dialog.destroy()
            self.perform_update()
            
        def cancel():
            dialog.destroy()
            
        tk.Button(
            button_frame,
            text="Update Now",
            command=update,
            bg='#4CAF50',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Later",
            command=cancel,
            bg='#f44336',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.mainloop()
        
    def perform_update(self):
        """Perform the update process"""
        try:
            # Create a backup of the current installation
            self.create_backup()
            
            # Download and install the new version
            self.download_and_install_update()
            
            # Show success message
            messagebox.showinfo(
                "Update Complete",
                "The software has been updated successfully!\n"
                "Please restart the application to apply the changes."
            )
            
            # Restart the application
            self.restart_application()
            
        except Exception as e:
            messagebox.showerror(
                "Update Failed",
                f"An error occurred during the update:\n{str(e)}\n\n"
                "Please contact support for assistance."
            )
            
    def create_backup(self):
        """Create a backup of the current installation"""
        # Implementation depends on your backup strategy
        pass
        
    def download_and_install_update(self):
        """Download and install the new version"""
        # Implementation depends on your update distribution method
        pass
        
    def restart_application(self):
        """Restart the application"""
        if platform.system() == 'Windows':
            subprocess.Popen([sys.executable] + sys.argv)
        else:
            os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit() 