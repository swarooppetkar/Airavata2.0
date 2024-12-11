import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime
import json  # Add this import statement
import tkinter.filedialog as filedialog
# other imports...

class Console:
    def __init__(self, parent):
        # Console frame
        self.frame = tk.Frame(parent, bg="#333")
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        self.logs = []  # Initialize logs as an empty list

        # Console text area
        self.console = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, height=8, bg="#1e1e1e", fg="white", font=("Segoe UI", 10), state="disabled")
        self.console.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Tag configurations for different log levels
        self.console.tag_config("debug", foreground="gray")
        self.console.tag_config("info", foreground="lightgreen")
        self.console.tag_config("success", foreground="lightblue")
        self.console.tag_config("warning", foreground="yellow")
        self.console.tag_config("error", foreground="orange")
        self.console.tag_config("critical", foreground="red")

        # Toolbar with console buttons
        self.toolbar = tk.Frame(self.frame, bg="#333")
        self.toolbar.pack(fill=tk.X)

        self.clear_button = tk.Button(self.toolbar, text="Clear", command=self.clear, bg="#444", fg="white")
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.export_button = tk.Button(self.toolbar, text="Export Logs", command=self.export_logs, bg="#444", fg="white")
        self.export_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.filter_label = tk.Label(self.toolbar, text="Filter:", bg="#333", fg="white")
        self.filter_label.pack(side=tk.LEFT, padx=5)

        self.log_level = tk.StringVar(value="All")
        self.filter_menu = tk.OptionMenu(self.toolbar, self.log_level, "All", "Debug", "Info", "Success", "Warning", "Error", "Critical", command=self.apply_filter)
        self.filter_menu.config(bg="#444", fg="white", width=10)
        self.filter_menu.pack(side=tk.LEFT, padx=5)

        self.search_label = tk.Label(self.toolbar, text="Search:", bg="#333", fg="white")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.toolbar, bg="#555", fg="white", width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.search)

    def log(self, message, level="info"):
        """Logs a message with a specified level."""
        self.console.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}\n"
        self.console.insert(tk.END, formatted_message, level)
        self.console.yview(tk.END)
        self.console.config(state="disabled")
        
        # Store the log message in self.logs
        self.logs.append((timestamp, level, message))


    def clear(self):
        """Clears the console."""
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")

    def export_logs(self):
        """Exports console logs to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                logs = self.console.get("1.0", tk.END).strip()
                file.write(logs)
            self.log("Logs exported successfully.", level="success")

    def apply_filter(self, event=None):
        """Applies a filter to show only selected log levels."""
        level = self.log_level.get().lower()
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)

        for line in self.logs:
            timestamp, log_level, message = line
            if level == "all" or log_level == level:
                tag = log_level
                formatted_message = f"[{timestamp}] [{log_level.upper()}] {message}\n"
                self.console.insert(tk.END, formatted_message, tag)

        self.console.config(state="disabled")
        self.console.yview(tk.END)

    def search(self, event=None):
        """Searches the console logs for a query."""
        query = self.search_entry.get().strip().lower()
        if query:
            self.console.tag_remove("highlight", "1.0", tk.END)
            start_pos = "1.0"
            while True:
                start_pos = self.console.search(query, start_pos, stopindex=tk.END, nocase=True)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(query)}c"
                self.console.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos
            self.console.tag_config("highlight", background="yellow", foreground="black")
