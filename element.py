import tkinter as tk
from PIL import Image, ImageTk  # To load and resize images for icons
import os
import json  # Add this import statement
import tkinter.filedialog as filedialog
# other imports...


class Element:
    def __init__(self, canvas, name, icon_path):
        self.canvas = canvas
        self.name = name
        self.x = 100  # Default X position
        self.y = 100  # Default Y position
        self.label = name  # Set the name as label
        self.icon_path = icon_path  # Path to the element's icon
        self.icon = None
        self.inlet_port = None
        self.outlet_port = None
        self.label_id = None
        self.selected = False  # Track if the element is selected for dragging
        self.rect_item = None  # Initialize rect_item for rectangle
        self.icon_item = None  # Icon item for the canvas
        self.highlight_rect = None  # Highlight rectangle

    def to_data(self):
        """Returns the element's data as a dictionary for saving."""
        return {
            "class": "Element:",
            "name": self.name,
            "x": self.x,
            "y": self.y
        }

    def load_from_data(self, data):
        """Loads data from a dictionary for initializing the element."""
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        # Implement the logic to re-create the element on the canvas

        # Bind canvas click event to remove highlight when clicking outside
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def create(self):
        """Create the element on the canvas."""
        # Load and resize the icon
        img = Image.open(self.icon_path)
        img = img.resize((60, 40), Image.LANCZOS)  # Resize the icon to fit the element
        self.icon = ImageTk.PhotoImage(img)
        
        # Create the element icon on the canvas
        self.icon_item = self.canvas.create_image(self.x + 30, self.y + 20, image=self.icon)
        self.label_id = self.canvas.create_text(self.x + 30, self.y - 10, text=self.label, fill="black")
        
        # Create ports (inlet and outlet)
        self.inlet_port = self.canvas.create_rectangle(self.x - 10, self.y + 20, self.x, self.y + 30, fill="black")
        self.outlet_port = self.canvas.create_rectangle(self.x + 50, self.y + 20, self.x + 60, self.y + 30, fill="white")
        
        # Create a rectangle to highlight the element on click, properly aligned around the icon
        self.rect_item = self.canvas.create_rectangle(
            self.x, self.y, self.x + 60, self.y + 40, outline="blue", width=2, state="hidden"
        )

        # Bind mouse events for interaction
        self.canvas.tag_bind(self.icon_item, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.icon_item, "<Double-1>", self.on_double_click)
        self.canvas.tag_bind(self.icon_item, "<B1-Motion>", self.on_drag_motion)  # Bind drag motion
        self.canvas.tag_bind(self.icon_item, "<ButtonRelease-1>", self.on_drag_release)  # Release drag

    def apply_highlight(self):
        """Apply highlight to the element."""
        self.canvas.itemconfig(self.icon, outline="red", width=3)  # Example: red border for highlight


    def remove_highlight(self):
        """Remove the highlight from the element."""
        self.canvas.itemconfig(self.icon, outline="black", width=1)  # Remove the highlight

    def on_click(self, event):
        """Highlight the rectangle when the icon is clicked."""
        # Initialize highlighted_element if it doesn't exist
        if not hasattr(self.canvas, 'highlighted_element'):
            self.canvas.highlighted_element = None

        # If this element is already highlighted, do nothing
        if self.canvas.highlighted_element == self:
            return

        # Remove highlight from previously selected element (if any)
        if self.canvas.highlighted_element:
            self.canvas.highlighted_element.remove_highlight()

        # Set the current element as the highlighted one
        self.canvas.highlighted_element = self
        
        # Create a highlight rectangle if not already created
        if not self.highlight_rect:
            self.highlight_rect = self.canvas.create_rectangle(self.x - 20, self.y - 20, self.x + 80, self.y + 60, outline="blue", width=2)

        # Show rectangle on click and highlight it
        self.canvas.itemconfig(self.highlight_rect, state="normal")  # Show the highlight rectangle

    def on_drag_motion(self, event):
        """Handle dragging motion of the element."""
        dx = event.x - self.x - 30  # Calculate the offset for movement
        dy = event.y - self.y - 20
        
        # Move the icon
        self.canvas.move(self.icon_item, dx, dy)
        self.canvas.move(self.label_id, dx, dy)
        self.canvas.move(self.inlet_port, dx, dy)
        self.canvas.move(self.outlet_port, dx, dy)
        self.canvas.move(self.rect_item, dx, dy)  # Move the rectangle along with the icon
        
        # Update the position of the element
        self.x = event.x - 30
        self.y = event.y - 20

        # Move the highlight rectangle to the new position as well
        if self.highlight_rect:
            self.canvas.coords(self.highlight_rect, self.x - 20, self.y - 20, self.x + 80, self.y + 60)

    def on_drag_release(self, event):
        """Handle drag release."""
        # Once drag is released, update the element's position
        self.x = event.x - 30
        self.y = event.y - 20

    def on_double_click(self, event):
        """Handle double-click events (open properties dialog)."""
        print(f"Double-clicked: {self.label}")
        self.open_properties_dialog()

    def open_properties_dialog(self):
        """Open a dialog to edit properties of the element."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")

        # Header
        tk.Label(dialog, text=f"Edit properties of {self.label}").pack()

        # Dictionary to store user input fields
        user_inputs = {}

        # Define element-specific properties dynamically
        element_properties = {
            "InletReservoir": ["flow_rate", "temperature"],
            "Pipe": ["inlet_port", "outlet_port"],
            "Valve": ["pressure", "diameter"],
            "Turbine": ["flow_rate", "efficiency"],
            "SurgeTank": ["capacity"],
            # Add properties for other elements as needed
        }

        # Get the properties for the current element class
        class_name = self.__class__.__name__
        if class_name in element_properties:
            for prop in element_properties[class_name]:
                current_value = getattr(self, prop, "")  # Get current value or default to ""
                user_inputs[prop] = self.add_property_field(dialog, prop.replace("_", " ").capitalize(), current_value)

        # Save button functionality
        def save_properties():
            for prop, entry in user_inputs.items():
                new_value = entry.get()  # Get the value from the entry field
                setattr(self, prop, new_value)  # Update the element's attribute dynamically
            dialog.destroy()  # Close the dialog

        # Add Save and Cancel buttons
        tk.Button(dialog, text="Save", command=save_properties).pack()
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def add_property_field(self, parent, label_text, value):
        """Add a label and entry field for a property."""
        tk.Label(parent, text=label_text).pack()
        entry = tk.Entry(parent)
        entry.insert(0, value)  # Prepopulate with the current value
        entry.pack()
        return entry

    def remove_highlight(self):
        """Remove the highlight from the selected item."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
            self.highlight_rect = None  # Clear the highlight rectangle

    def remove_highlight_on_outside_click(self, event):
        """Remove highlight if click is outside of any element."""
        if hasattr(self.canvas, 'highlighted_element') and self.canvas.highlighted_element:
            bbox = self.canvas.bbox(self.canvas.highlighted_element.highlight_rect)
            if not bbox or not (bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]):
                self.canvas.highlighted_element.remove_highlight()
                del self.canvas.highlighted_element  # Clear the reference

    def on_canvas_click(self, event):
        """Remove highlight from the selected element when clicking outside."""
        self.remove_highlight_on_outside_click(event)


# Global variable to store the selected element
selected_element = None

class InletReservoir(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/inlet_reservoir_icon.png")
        self.level_h = ""  # Default value for Level H
        self.pipe_z = ""  # Default value for Pipe Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/inlet_reservoir_image.png"  # Path to display image in the dialog

    def to_data(self):
        return {
            "class": "InletReservoir",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "level_h": self.level_h,
            "pipe_z": self.pipe_z,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.level_h = data.get("level_h", "")
        self.pipe_z = data.get("pipe_z", "")

    def open_properties_dialog(self):
        """Open a beautiful, centered dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 400, 400
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Level H [m asl]": "level_h",
            "Pipe Z [m asl]": "pipe_z",
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons at the bottom
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Save", font=button_font, command=lambda: self.save_properties(user_inputs, dialog)).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Cancel", font=button_font, command=dialog.destroy).pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()




class Pipe(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/pipe_icon.png")
        self.diameter = ""  # Diameter D [m]
        self.length = ""    # Length L [m]
        self.celerity = ""  # Celerity a [m/s]
        self.manning_n = "" # Manning n [...]
        self.inlet_h1 = ""  # Inlet H1 [m]
        self.inlet_q1 = ""  # Inlet Q1 [m³/s]
        self.nodes_n = ""   # Nodes N [-]
        self.dt_max = "0.0" # dt max [s], constant value
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/Pipe_image.png"  # Path to display image in the dialog
        # Placeholder for the additional functionality
        self.source_pipe = None  # Reference to another Pipe for copying values

    def to_data(self):
        """Serialize the Pipe properties into a dictionary."""
        return {
            "class": "Pipe",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "length": self.length,
            "celerity": self.celerity,
            "manning_n": self.manning_n,
            "inlet_h1": self.inlet_h1,
            "inlet_q1": self.inlet_q1,
            "nodes_n": self.nodes_n,
            "dt_max": self.dt_max,
            "source_pipe": self.source_pipe.name if self.source_pipe else None
        }

    def load_from_data(self, data):
        """Load Pipe properties from a dictionary."""
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.diameter = data.get("diameter", "")
        self.length = data.get("length", "")
        self.celerity = data.get("celerity", "")
        self.manning_n = data.get("manning_n", "")
        self.inlet_h1 = data.get("inlet_h1", "")
        self.inlet_q1 = data.get("inlet_q1", "")
        self.nodes_n = data.get("nodes_n", "")
        self.dt_max = data.get("dt_max", "0.0")
        # Placeholder for source_pipe loading logic, if needed later

    def open_properties_dialog(self):
        """Open a dialog for editing Pipe properties."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with main window
        dialog.grab_set()  # Prevent interaction with other windows
        dialog.focus_set()

        # Center dialog on the screen
        width, height = 550, 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)

        # Display image
        img = Image.open("C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/pipe_image.png")
        img = img.resize((300, 250), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(dialog, image=img_tk)
        img_label.image = img_tk
        img_label.pack()

        # Properties to edit
        properties = {
            "Diameter D [m]": "diameter",
            "Length L [m]": "length",
            "Celerity a [m/s]": "celerity",
            "Manning n [...]": "manning_n",
            "Inlet H1 [m]": "inlet_h1",
            "Inlet Q1 [m³/s]": "inlet_q1",
            "Nodes N [-]": "nodes_n",
            "dt max <= [s]": "dt_max",
        }

        # Input fields for properties
        user_inputs = {}
        for label, attr in properties.items():
            field_frame = tk.Frame(dialog)
            field_frame.pack(fill=tk.X, pady=5)
            tk.Label(field_frame, text=label, font=label_font).pack(side=tk.LEFT)
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attr, ""))
            entry.pack(side=tk.RIGHT)
            user_inputs[attr] = entry

        # Placeholder for selecting source pipe
        tk.Label(dialog, text="Copy values from another Pipe:", font=label_font).pack(pady=5)
        tk.Button(dialog, text="Select Pipe", command=lambda: self.select_source_pipe()).pack(pady=5)

        # Save and Cancel buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Save", command=lambda: self.save_properties(user_inputs, dialog)).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attr, entry in user_inputs.items():
            setattr(self, attr, entry.get())
        dialog.destroy()

    def select_source_pipe(self):
        """Placeholder for selecting a source pipe."""
        pass



class OutletReservoir(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/outlet_reservoir_icon.png")
        self.level_h = ""  # Default value for Level H
        self.level_z = ""  # Default value for Level Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/inlet_outletReservior_image.png"  # Path to display image in the dialog

    def to_data(self):
        return {
            "class": "OutletReservoir",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "level_h": self.level_h,
            "level_z": self.level_z,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.level_h = data.get("level_h", "")
        self.level_z = data.get("level_z", "")

    def open_properties_dialog(self):
        """Open a beautiful, centered dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 400, 400
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Level H [m asl]": "level_h",
            "Level Z [m asl]": "level_z",
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons at the bottom
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Save", font=button_font, command=lambda: self.save_properties(user_inputs, dialog)).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Cancel", font=button_font, command=dialog.destroy).pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()




class Valve(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/valve_icon.png")
        self.diameter = "0.0"  # Default value for Diameter (D)
        self.loss_coefficient = "0.0"  # Default value for Loss Coefficient (Kv)
        self.loss_factor = "0.0"  # Default value for Loss Factor (n)
        self.elevation_z = "0.0"  # Default value for Elevation Z
        self.custom_values = []  # Holds the 2-column sheet values
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/valve_image.png"  # Path to the provided image

    def to_data(self):
        return {
            "class": "Valve",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "loss_coefficient": self.loss_coefficient,
            "loss_factor": self.loss_factor,
            "elevation_z": self.elevation_z,
            "custom_values": self.custom_values,  # Save sheet data
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.diameter = data.get("diameter", "0.0")
        self.loss_coefficient = data.get("loss_coefficient", "0.0")
        self.loss_factor = data.get("loss_factor", "0.0")
        self.elevation_z = data.get("elevation_z", "0.0")
        self.custom_values = data.get("custom_values", [])

    def open_properties_dialog(self):
        """Open a dynamic properties dialog for the Valve."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())
        dialog.grab_set()
        dialog.focus_set()

        # Set size and center the dialog
        width, height = 700, 600
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Main frame for layout
        main_frame = tk.Frame(dialog, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Image and input fields
        left_frame = tk.Frame(main_frame, bg="#ffffff", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        header_label = tk.Label(left_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0", anchor="w")
        header_label.pack(fill=tk.X, pady=(0, 10))

        # Display the image
        img = Image.open(self.image_path)
        img = img.resize((250, 200), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(left_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack(pady=(0, 10))

        # Properties to include in the dialog
        properties = {
            "Diameter D [m]": "diameter",
            "Loss Coefficient Kv": "loss_coefficient",
            "Loss Factor n": "loss_factor",
            "Elevation Z [m asl]": "elevation_z",
        }

        # Container for input fields
        inputs_frame = tk.Frame(left_frame, pady=10, padx=10, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Right side: Two-column sheet
        right_frame = tk.Frame(main_frame, bg="#f0f0f0", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a label for the sheet
        sheet_label = tk.Label(right_frame, text="t [s] vs y [-]", font=header_font, bg="#f0f0f0")
        sheet_label.pack(pady=(0, 10))

        # Sheet frame with colored background
        sheet_frame = tk.Frame(right_frame, bg="#d4f1f9", padx=5, pady=5, relief=tk.RIDGE, bd=2)
        sheet_frame.pack(fill=tk.BOTH, expand=True)

        # Table header
        tk.Label(sheet_frame, text="t [s]", font=label_font, bg="#9ae3ff").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(sheet_frame, text="y [-]", font=label_font, bg="#9ae3ff").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Create sheet entries
        sheet_entries = []
        for i in range(16):  # 16 rows
            t_entry = tk.Entry(sheet_frame, font=label_font, width=10, bg="#ffffff", justify="center")
            t_entry.grid(row=i + 1, column=0, padx=5, pady=2, sticky="ew")
            y_entry = tk.Entry(sheet_frame, font=label_font, width=10, bg="#ffffff", justify="center")
            y_entry.grid(row=i + 1, column=1, padx=5, pady=2, sticky="ew")

            # Pre-fill values if available
            if i < len(self.custom_values):
                t_entry.insert(0, self.custom_values[i][0])
                y_entry.insert(0, self.custom_values[i][1])

            sheet_entries.append((t_entry, y_entry))

        # Bottom: Buttons
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(button_frame, text="Save", font=button_font, command=lambda: self.save_properties(user_inputs, sheet_entries, dialog)).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Cancel", font=button_font, command=dialog.destroy).pack(side=tk.RIGHT, padx=20)


    def save_properties(self, user_inputs, sheet_entries, dialog):
        """Save the properties and the sheet values, then close the dialog."""
        # Save the main properties
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())

        # Save the sheet values
        self.custom_values = []
        for t_entry, y_entry in sheet_entries:
            t_value = t_entry.get()
            y_value = y_entry.get()
            if t_value or y_value:  # Save only non-empty rows
                self.custom_values.append((t_value, y_value))

        dialog.destroy()




class Manifold(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/manifold_icon.png")
        self.elev_z = ""  # Default value for Elev. Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/Manifold_image.png"  # Path to display image in the dialog

    def to_data(self):
        return {
            "class": "Manifold",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "elev_z": self.elev_z,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.elev_z = data.get("elev_z", "")

    def open_properties_dialog(self):
        """Open a dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 400, 350
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Elev. Z [m asl]": "elev_z",
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons at the bottom
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Save", font=button_font, command=lambda: self.save_properties(user_inputs, dialog)).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Cancel", font=button_font, command=dialog.destroy).pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()




class SurgeTank(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/surge_tank_icon.png")
        self.throttle_ao = ""  # Throttle Ao [m2]
        self.stank_a = ""      # S-tank A [m2]
        self.throttle_kin = ""  # Throttle Kin
        self.throttle_kout = ""  # Throttle Kout
        self.throttle_el_zo = ""  # Throttle el. Zo [m3/s]
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project/Icons/surge_tank_image.png"  # Image to display in dialog

    def to_data(self):
        return {
            "class": "SurgeTank",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "throttle_ao": self.throttle_ao,
            "stank_a": self.stank_a,
            "throttle_kin": self.throttle_kin,
            "throttle_kout": self.throttle_kout,
            "throttle_el_zo": self.throttle_el_zo,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.throttle_ao = data.get("throttle_ao", "")
        self.stank_a = data.get("stank_a", "")
        self.throttle_kin = data.get("throttle_kin", "")
        self.throttle_kout = data.get("throttle_kout", "")
        self.throttle_el_zo = data.get("throttle_el_zo", "")

    def open_properties_dialog(self):
        """Open a centered dialog to edit SurgeTank properties."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())
        dialog.grab_set()
        dialog.focus_set()

        # Set size and center the dialog
        width, height = 400, 600
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((250, 250), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include
        properties = {
            "Throttle Ao [m2]": "throttle_ao",
            "S-tank A [m2]": "stank_a",
            "Throttle Kin": "throttle_kin",
            "Throttle Kout": "throttle_kout",
            "Throttle el. Zo [m3/s]": "throttle_el_zo",
        }

        # Inputs frame
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            entry = tk.Entry(field_frame, font=label_font, width=20)
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Save", font=button_font, command=lambda: self.save_properties(user_inputs, dialog)).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Cancel", font=button_font, command=dialog.destroy).pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, dialog):
        """Save properties and close dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()







class Turbine:
    def __init__(self, canvas, name=None):
        self.canvas = canvas
        self.name = name or "Turbine"
        self.parent = parent  # Store the parent reference
        self.image_path_main = "/path/to/your/main/image.png"  # Replace with actual image path
        self.image_path_governor = "/path/to/your/governor/image.png"  # Replace with actual image path
        self.properties = {
            "Main": {
                "Ho [m]": 0.0,
                "Qo [m³/s]": 0.0,
                "Do [m]": 0.0,
                "No [rpm]": 0.0,
                "Jn [kgm²]": 0.0,
                "Efficiency np [pu]": 0.9,
                "Z elev [m asl]": 0.0,
                "Select": "Francis 23"
            },
            "Governor": {
                "ΔP [% of Rated]": -100.0,
                "T load Rej [s]": 0.0,
                "Δt ramp [s]": 0.1,
                "Tg [s]": 0.0,
                "Td [s]": 0.0,
                "Tr [s]": 0.0,
                "bp [-]": 0.0
            }
        }

        # Call to open the properties dialog
        self.open_properties_dialog()


    def open_properties_dialog(self):
        """Create and display the turbine properties dialog."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Turbine Properties")
        dialog.geometry("800x600")
        dialog.resizable(False, False)

        # Create tabs
        tab_control = ttk.Notebook(dialog)
        main_tab = ttk.Frame(tab_control)
        governor_tab = ttk.Frame(tab_control)

        tab_control.add(main_tab, text="Main")
        tab_control.add(governor_tab, text="Governor")
        tab_control.pack(expand=True, fill=tk.BOTH)

        # Main Tab
        self.setup_main_tab(main_tab)

        # Governor Tab
        self.setup_governor_tab(governor_tab)

        # Save and Cancel Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)

        save_button = tk.Button(button_frame, text="Save", bg="green", fg="white", command=self.save_properties)
        save_button.pack(side="left", padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", bg="red", fg="white", command=dialog.destroy)
        cancel_button.pack(side="right", padx=10)

    def setup_main_tab(self, tab):
        """Setup the 'Main' tab."""
        # Top section with images
        image_frame = tk.Frame(tab)
        image_frame.pack(fill=tk.X, pady=10)

        img = Image.open(self.image_path_main)
        img = img.resize((350, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk)
        img_label.image = img_tk
        img_label.pack(side=tk.LEFT, padx=10)

        # Data section
        data_frame = tk.Frame(tab)
        data_frame.pack(fill=tk.X, pady=10)

        for field, value in self.properties["Main"].items():
            field_frame = tk.Frame(data_frame)
            field_frame.pack(fill=tk.X, pady=5)

            label = tk.Label(field_frame, text=field, width=20, anchor="w")
            label.pack(side=tk.LEFT, padx=5)

            if field == "Select":
                combo = ttk.Combobox(field_frame, values=["Francis 23", "Kaplan", "Pelton"], width=15)
                combo.set(value)
                combo.pack(side=tk.RIGHT, padx=5)
                self.properties["Main"][field] = combo
            else:
                entry = tk.Entry(field_frame, width=20)
                entry.insert(0, value)
                entry.pack(side=tk.RIGHT, padx=5)
                self.properties["Main"][field] = entry

    def setup_governor_tab(self, tab):
        """Setup the 'Governor' tab."""
        # Top section with diagrams
        top_frame = tk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=10)

        img = Image.open(self.image_path_governor)
        img = img.resize((350, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(top_frame, image=img_tk)
        img_label.image = img_tk
        img_label.pack(side=tk.LEFT, padx=10)

        # Data section
        data_frame = tk.Frame(tab)
        data_frame.pack(fill=tk.X, pady=10)

        for field, value in self.properties["Governor"].items():
            field_frame = tk.Frame(data_frame)
            field_frame.pack(fill=tk.X, pady=5)

            label = tk.Label(field_frame, text=field, width=20, anchor="w")
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(field_frame, width=20)
            entry.insert(0, value)
            entry.pack(side=tk.RIGHT, padx=5)
            self.properties["Governor"][field] = entry

    def save_properties(self):
        """Save properties from the dialog."""
        for tab, fields in self.properties.items():
            for field, widget in fields.items():
                if isinstance(widget, tk.Entry):
                    fields[field] = widget.get()
                elif isinstance(widget, ttk.Combobox):
                    fields[field] = widget.get()

        print("Properties Saved:", self.properties)


# Test the UI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hydraulic Simulator")
    turbine = Turbine(root)
    root.mainloop()


