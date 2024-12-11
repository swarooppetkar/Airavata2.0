import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import os
from console import Console
from file_manager import FileManager
from transient_simulation import TransientSimulation
import psutil
from whiteboard import Whiteboard
import json  # Add this import statement
import tkinter.filedialog as filedialog
# other imports...


class AiravataSoftware:
    def __init__(self, root):
        self.root = root
        self.root.title("Airavata 2.0")
        self.root.geometry("1000x700")
        self.current_theme = 'dark'
        self.root.config(bg="#333")
        self.file_saved = False
        self.file_open = False
        self.elements = []
        self.simulation = None
        self.file_manager = FileManager()  # Initialize FileManager
        if not self.file_manager:
            print("File manager is not initialized.")
            return
        self.whiteboard = Whiteboard(root)
        self.current_file_name = None
        self.highlighted_element = None

        # Create UI components
        self.create_file_label()
        self.create_toolbar()
        self.create_console()
        self.create_whiteboard()

        # Apply dark theme as default
        self.apply_dark_theme(show_message=False)

    def create_file_label(self):
        """Label to display the current file's name."""
        self.file_label = tk.Label(self.root, text="No file opened", bg="#f5f5f5", anchor="w", font=("Segoe UI", 10))
        self.file_label.pack(fill=tk.X)

    def update_file_label(self):
        """Update the file label to show the current file name."""
        if self.current_file_name:
            self.file_label.config(text=f"Current File: {os.path.basename(self.current_file_name)}")
        else:
            self.file_label.config(text="No file opened")


    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#e0e0e0", pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Load Icons
        self.new_icon = self.load_and_resize_icon("Icons/new_icon.png")
        self.open_icon = self.load_and_resize_icon("Icons/open_icon.png")
        self.save_icon = self.load_and_resize_icon("Icons/save_icon.png")
        self.close_icon = self.load_and_resize_icon("Icons/close_icon.png")
        self.info_icon = self.load_and_resize_icon("Icons/info_icon.png")
        self.export_icon = self.load_and_resize_icon("Icons/export_icon.png")
        self.theme_icon = self.load_and_resize_icon("Icons/theme_icon.png")
        self.performance_icon = self.load_and_resize_icon("Icons/performance_icon.png")
        self.clear_screen_icon = self.load_and_resize_icon("Icons/clear_screen_icon.png")

        # Add toolbar buttons
        self.add_toolbar_button(toolbar, self.new_icon, "New File", self.create_new_file)
        self.add_toolbar_button(toolbar, self.open_icon, "Open File", self.open_file)
        self.add_toolbar_button(toolbar, self.save_icon, "Save File", self.save_file)
        self.add_toolbar_button(toolbar, self.close_icon, "Terminate File", self.terminate_file)
        self.add_toolbar_button(toolbar, self.info_icon, "File Info", self.show_file_info)
        self.add_toolbar_button(toolbar, self.export_icon, "Export Excel", self.export_to_excel)
        self.add_toolbar_button(toolbar, self.theme_icon, "Toggle Theme", self.toggle_theme)
        self.add_toolbar_button(toolbar, self.performance_icon, "Monitor Performance", self.monitor_performance)
        self.add_toolbar_button(toolbar, self.clear_screen_icon, "Clear Screen", self.clear_screen)

    def create_console(self):
        self.console_frame = tk.Frame(self.root, bg="#f5f5f5", bd=2, relief="sunken")
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.console = Console(self.console_frame)
        self.console.frame.pack(fill=tk.X)

    def create_whiteboard(self):
        self.whiteboard_frame = tk.Frame(self.root)
        self.whiteboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.whiteboard = Whiteboard(self.whiteboard_frame)
        self.whiteboard.pack(fill=tk.BOTH, expand=True)

        # Initially disable the whiteboard
        self.whiteboard_disabled = False

    def enable_whiteboard(self):
        """Enable the whiteboard interactions."""
        self.whiteboard_disabled = False

    def disable_whiteboard(self):
        """Disable the whiteboard interactions."""
        self.whiteboard_disabled = True

    def load_and_resize_icon(self, icon_path, size=(32, 32)):
        img = Image.open(icon_path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def add_toolbar_button(self, toolbar, icon, tooltip_text, command):
        button = tk.Button(toolbar, image=icon, command=command, relief=tk.FLAT, bg="#e0e0e0", borderwidth=0)
        button.pack(side=tk.LEFT, padx=4)
        button.bind("<Enter>", lambda event, text=tooltip_text: self.show_tooltip(event, text))
        button.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, text):
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self.tooltip = Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, background="lightyellow", font=("Segoe UI", 10), relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            self.tooltip = None

    def create_new_file(self):
        if self.file_open:
            messagebox.showwarning("Warning", "Close the current file before creating a new one.")
        else:
            file_name = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
            if file_name:
                # Create a new, empty file
                with open(file_name, 'w') as new_file:
                    new_file.write("{}")  # Optionally initialize with default JSON content (empty JSON object)
                self.file_manager = FileManager(os.path.dirname(file_name))
                self.file_saved = False
                self.file_open = True
                self.current_file_name = file_name  # Set the current file name
                self.whiteboard.is_file_open = True  # Enable the whiteboard
                self.whiteboard.clear()  # Clear the whiteboard
                self.update_file_label()  # Update the file label
                self.console.log("New file created successfully.",level="success")

    def open_file(self):
        """Open a file and load its content onto the canvas."""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            messagebox.showinfo("No File Selected", "No file was selected.")
            return

        try:
            # Load elements from the selected file
            with open(file_path, 'r') as file:
                elements_data = json.load(file)
            
            if not isinstance(elements_data, dict) or 'elements' not in elements_data:
                raise ValueError("Invalid file structure. Expected a dictionary with an 'elements' key.")
            
            # Clear existing elements before loading new ones
            self.whiteboard.clear()

            # Load elements into the canvas
            self.whiteboard.load_elements(elements_data['elements'])

            # Update file state
            self.current_file_name = file_path
            self.file_open = True  # Set the file open flag
            self.whiteboard.is_file_open = True  # Enable the whiteboard
            self.file_manager.file_path = file_path  # Update the file manager
            self.update_file_label()  # Update the file label
            self.console.log(f"Successfully loaded file: {os.path.basename(file_path)}",level="success")

            messagebox.showinfo("File Loaded", f"Successfully loaded file: {os.path.basename(file_path)}")

        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("File Error", f"Failed to load the file. Error: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")


    def save_file(self):
        if self.current_file_name:
            self.file_manager.save_elements(
                self.current_file_name,
                [element.to_data() for element in self.whiteboard.elements]
            )
            self.console.log(
                f"File saved successfully: {os.path.basename(self.current_file_name)}",
                level="success",
            )
        else:
            file_path = filedialog.asksaveasfilename(
                title="Save File",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
            )

            if file_path:
                self.file_manager.file_path = file_path
                self.current_file_name = file_path
                self.file_manager.save_elements(
                    file_path, [element.to_data() for element in self.whiteboard.elements]
                )
                self.console.log(
                    f"File saved successfully: {os.path.basename(file_path)}",
                    level="success",
                )
            else:
                self.console.log("No file selected for saving.", level="error")




    def terminate_file(self):
        """Terminate the current file."""
        if self.file_open:
            self.file_manager.close_file()  # Clear file-related data
            self.simulation = None
            self.file_saved = False
            self.file_open = False
            self.whiteboard.is_file_open = False  # Disable the whiteboard
            self.whiteboard.clear()  # Clear the whiteboard
            self.current_file_name = None  # Reset the current file name
            self.update_file_label()  # Update the file label
            self.console.log("File terminated successfully.",level="success")
        else:
            self.root.quit()



    def clear_screen(self):
        self.whiteboard.clear()
        # Clear the console if you want to
        #self.console.clear()

    def show_file_info(self):
        info_window = Toplevel(self.root)
        info_window.title("File Information")

        # Set size of the window
        width, height = 400, 300
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry(f"{width}x{height}+{x}+{y}")  # Center the window on the screen
        info_window.resizable(False, False)  # Disable resizing

        # Ensure the dialog is modal and focused
        info_window.transient(self.root)  # Associate with the main window
        info_window.grab_set()  # Prevent interaction with other windows until this one is closed
        info_window.focus_set()  # Automatically focus on the info window

        info_text = """
        ❖ Problem Statement ID : SIH1693
        ❖ Problem Statement Title: Developing a Robust Hydraulic Transient Analysis Model.
        ❖ Theme : Smart Automation
        ❖ Team ID : 36652
        ❖ Team Name : AIRAVATA
        """
        info_label = tk.Label(info_window, text=info_text, padx=10, pady=10, font=("Segoe UI", 10))
        info_label.pack(fill=tk.BOTH, expand=True)



    def export_to_excel(self):
        if self.simulation:
            data = self.simulation.method_of_characteristics()
            output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
            if output_path:
                self.file_manager.export_to_excel(data, output_path)
                self.console.log("Exported project to Excel successfully.",level="success")
        else:
            messagebox.showwarning("Warning", "No project data to export.")

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self, show_message=True):
        """Applies the dark theme to the application."""
        self.root.config(bg="#333")
        self.console.frame.config(bg="#333")
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(fg="#f5f5f5", bg="#333")
            elif isinstance(widget, tk.Button):
                widget.config(fg="#f5f5f5", bg="#333")
        self.current_theme = 'dark'
        if show_message:
            messagebox.showinfo("Theme", "Switched to Dark mode.")


    def apply_light_theme(self):
        self.root.config(bg="#f5f5f5")
        self.console.frame.config(bg="#f5f5f5")
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(fg="#000000", bg="#f5f5f5")
            elif isinstance(widget, tk.Button):
                widget.config(fg="#000000", bg="#f5f5f5")
        self.current_theme = 'light'
        messagebox.showinfo("Theme", "Switched to Light mode.")

    def on_element_click(self, event):
        """Handles left-click events to select or highlight an element."""
        item = self.canvas.find_closest(event.x, event.y)
        item_type = self.canvas.type(item)

        if self.highlighted_element:
            self.highlighted_element.remove_highlight()

        if item_type == 'rectangle':
            for element in self.elements:
                if element.icon == item:
                    self.highlighted_element = element
                    self.highlighted_element.apply_highlight()
                    break

    def highlight_element(self, element):
        if self.highlighted_element:
            self.whiteboard.remove_highlight(self.highlighted_element)

        self.highlighted_element = element
        self.whiteboard.highlight_element(element)
        self.console.log(f"Element {element.label} highlighted.",level="info")

    def monitor_performance(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        net_info = psutil.net_io_counters()
        battery = psutil.sensors_battery()
        battery_status = "Charging" if battery and battery.power_plugged else "Not Charging"
        battery_percentage = battery.percent if battery else "N/A"
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_usage = ", ".join([f"GPU {gpu.id}: {gpu.memoryUtil * 100:.2f}% used" for gpu in gpus])
        except ImportError:
            gpu_usage = "GPU monitoring not available"
        
        processes = [(p.info['pid'], p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent'])]
        processes = sorted(processes, key=lambda x: x[2], reverse=True)[:5]
        process_info = "\n".join([f"PID: {pid}, Name: {name}, CPU Usage: {cpu}%" for pid, name, cpu in processes])

        messagebox.showinfo("Performance Monitoring", 
                            f"CPU Usage: {cpu_usage}%\n"
                            f"Memory Usage: {memory_info.percent}%\n"
                            f"Disk Usage: {disk_info.percent}%\n"
                            f"Network - Sent: {net_info.bytes_sent} bytes, Received: {net_info.bytes_recv} bytes\n"
                            f"Battery Status: {battery_status} ({battery_percentage}%)\n"
                            f"GPU Usage: {gpu_usage}\n"
                            f"Top 5 Processes by CPU Usage:\n{process_info}")

        self.console.log(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%",level="info")

def show_splash_screen(root, on_splash_close):
    splash = Toplevel(root)
    splash.title("Airavata Loading")
    splash.geometry("800x600")
    splash.overrideredirect(True)
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    splash.geometry(f"800x600+{x}+{y}")
    splash_image_path = "Icons/splash_image.png"
    splash_image = Image.open(splash_image_path)
    splash_image = splash_image.resize((800, 600), Image.LANCZOS)
    splash_photo = ImageTk.PhotoImage(splash_image)
    splash_label = tk.Label(splash, image=splash_photo)
    splash_label.image = splash_photo
    splash_label.pack(fill=tk.BOTH, expand=True)
    
    root.withdraw()  # Hide the main window during the splash screen
    splash.after(3000, lambda: on_splash_close(splash))


def on_splash_close(splash):
    splash.destroy()
    root.deiconify()  # Show the main window
    root.state("zoomed")  # Maximize the window after the splash screen
    app = AiravataSoftware(root) # Initialize the application



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")  # Set to full screen size
    root.state("normal")  # Ensure windowed mode, not fullscreen
    show_splash_screen(root, on_splash_close)
    app = AiravataSoftware(root)
    root.mainloop()

