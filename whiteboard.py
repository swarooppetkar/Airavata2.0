import tkinter as tk
from tkinter import simpledialog, messagebox
from element import InletReservoir, OutletReservoir, Valve, Manifold, SurgeTank, Turbine, Pipe
from file_manager import FileManager  # Assuming this manages file open/save
import os
import json  # Add this import statement
import tkinter.filedialog as filedialog




class Whiteboard(tk.Frame):
    def __init__(self, parent, project_folder=None):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Initialize a dictionary to keep track of element counts
        self.element_counts = {}
        # You may also need to track existing elements by name if necessary
        self.deleted_elements = set()  # Track deleted elements for each type
        # Initialize a counter for unique element names
        self.element_counter = 0
        # File-related attributes
        self.file_manager = FileManager(project_folder)  # Pass the project_folder to the FileManager
        self.current_file = None
        self.is_file_open = False

        # UI components
        self.elements = []  # List to hold created elements
        self.selected_element = None  # Currently selected element
        self.status_label = tk.Label(self, text=f"File Open: {self.file_manager.current_file}", bg="lightgrey", anchor="w")
        self.status_label.pack(fill=tk.X)

        self.create_context_menu()
        self.canvas.bind("<Button-3>", self.show_context_menu)  # Right-click for context menu
        self.canvas.bind("<Button-1>", self.on_click)  # Left-click for element selection

    def create_context_menu(self):
        """Creates the context menu for adding elements and other actions."""
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Inlet Reservoir", command=self.add_inlet_reservoir)
        self.context_menu.add_command(label="Outlet Reservoir", command=self.add_outlet_reservoir)
        self.context_menu.add_command(label="Valve", command=self.add_valve)
        self.context_menu.add_command(label="Manifold", command=self.add_manifold)
        self.context_menu.add_command(label="Surge Tank", command=self.add_surge_tank)
        self.context_menu.add_command(label="Turbine", command=self.add_turbine)
        self.context_menu.add_command(label="Pipe", command=self.add_Pipe)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Duplicate", command=self.duplicate_element)
        self.context_menu.add_command(label="Delete", command=self.delete_element)

    def show_context_menu(self, event):
        """Displays the context menu only if a file is open."""
        if not self.is_file_open:
            messagebox.showwarning("Action Denied", "Please open or create a file first.")
            return

        # Find the closest item on the canvas where the right-click occurred
        item = self.canvas.find_closest(event.x, event.y)

        # Check if the clicked item corresponds to any element
        if item:
            for element in self.elements:
                if element.icon_item == item[0]:
                    if self.selected_element:
                        self.selected_element.remove_highlight()  # Remove highlight from the previous selection
                    self.selected_element = element  # Set the clicked element as the selected element
                    element.apply_highlight()  # Apply highlight to the selected element
                    break

        # Show the context menu at the position where the right-click occurred
        self.context_menu.post(event.x_root, event.y_root)

    def add_element(self, element_class):
        """Generates a new element and adds it to the canvas."""
        if not self.is_file_open:
            messagebox.showwarning("Action Denied", "Please open or create a file first.")
            return

        # Initialize the counter for the element type if it's not already
        if element_class.__name__ not in self.element_counts:
            self.element_counts[element_class.__name__] = 0

        # Handle deletion adjustments: check if there are any deleted elements
        if self.deleted_elements:
            # Find the smallest deleted number and reuse it
            available_numbers = [
                int(name.split('_')[1].split()[0]) for name in self.deleted_elements if name.startswith(element_class.__name__)
            ]
            if available_numbers:
                next_available = min(available_numbers)
                name = f"{element_class.__name__}_{next_available}"
                
                # Check if the name is in the deleted list before removing it
                if name in self.deleted_elements:
                    self.deleted_elements.remove(name)  # Remove the name from deleted set
            else:
                self.element_counts[element_class.__name__] += 1
                name = f"{element_class.__name__}_{self.element_counts[element_class.__name__]}"
        else:
            # No deleted elements, continue as normal
            self.element_counts[element_class.__name__] += 1
            name = f"{element_class.__name__}_{self.element_counts[element_class.__name__]}"

        # Create and add the new element to the canvas
        name = self.get_new_element_name()
        element = element_class(self.canvas, name)  # Pass both canvas and name
        self.elements[name] = element
        element.create()
        self.elements.append(element)
        return element
    
    def get_new_element_name(self):
        """Generate a unique name for a new element."""
        self.element_counter += 1
        return f"Element_{self.element_counter}"


    def add_inlet_reservoir(self):
        self.add_element(InletReservoir)

    def add_Pipe(self):
        self.add_element(Pipe)

    def add_outlet_reservoir(self):
        self.add_element(OutletReservoir)

    def add_valve(self):
        self.add_element(Valve)

    def add_manifold(self):
        self.add_element(Manifold)

    def add_surge_tank(self):
        self.add_element(SurgeTank)

    def add_turbine(self):
        self.add_element(Turbine)

    def on_click(self, event):
        """Handles left-click events to select an element."""
        if not self.is_file_open:
            return

        item = self.canvas.find_closest(event.x, event.y)
        clicked_on_element = False

        for element in self.elements:
            if element.icon_item == item[0]:
                clicked_on_element = True
                if self.selected_element and self.selected_element != element:
                    self.selected_element.remove_highlight()
                self.selected_element = element
                element.apply_highlight()
                break

        if not clicked_on_element and self.selected_element:
            self.selected_element.remove_highlight()
            self.selected_element = None

    def duplicate_element(self):
        """Duplicate the currently selected element."""
        if self.selected_element:
            # Retrieve the element to be duplicated
            original_element = self.selected_element
            
            # Create a duplicate with a new name
            duplicate = type(original_element)(self.canvas, original_element.name + " (copy)")
            
            # Set the duplicate's position slightly offset to avoid overlap
            duplicate.x = original_element.x + 20
            duplicate.y = original_element.y + 20
            
            # Create the duplicate element
            duplicate.create()
            
            # Add it to the canvas or the list of elements
            self.elements.append(duplicate)
            
            # Optionally, set the newly created duplicate as the selected element
            self.selected_element = duplicate


    def delete_element(self):
        """Deletes the selected element from the canvas."""
        if self.selected_element:
            # Track the name of the element before deletion
            element_name = self.selected_element.name
            if element_name:
                # Add the element name to the deleted set (so it can be reused later)
                self.deleted_elements.add(element_name)

            # Proceed with the actual deletion
            items_to_delete = [
                self.selected_element.icon_item,
                self.selected_element.label_id,
                self.selected_element.inlet_port,
                self.selected_element.outlet_port,
                self.selected_element.rect_item,
                self.selected_element.highlight_rect,
            ]
            for item in items_to_delete:
                if item:
                    self.canvas.delete(item)

            self.elements.remove(self.selected_element)
            self.selected_element = None


    def clear(self):
        """Clears all elements from the whiteboard."""
        for element in self.elements[:]:
            self.selected_element = element
            self.delete_element()
        self.elements.clear()
        self.selected_element = None

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
        """Terminates the current file and clears the whiteboard."""
        if not self.is_file_open:
            messagebox.showwarning("Terminate Error", "No file is currently open.")
            return

        self.is_file_open = False
        self.current_file = None
        self.status_label.config(text="No file open")
        self.clear()

    def create_new_file(self):
        """Creates a new file, resets the current file state, and clears the whiteboard."""
        self.current_file = None  # Reset the current file state
        self.is_file_open = False
        self.status_label.config(text="No file open")  # Update the status
        self.clear()  # Clear the current whiteboard

    def load_elements(self, elements_data=None):
        """Load elements either from a file or directly passed data."""
        if elements_data is None:
            if not os.path.exists(self.file_path):
                print(f"Error: File does not exist: {self.file_path}")
                return

            with open(self.file_path, 'r') as file:
                try:
                    elements_data = json.load(file)
                except json.JSONDecodeError:
                    print("Error: The file content is not valid JSON.")
                    return

        if isinstance(elements_data, dict) and "elements" in elements_data:
            elements_data = elements_data["elements"]

        for element_data in elements_data:
            try:
                element_class = globals()[element_data["class"]]
                element = element_class(self.canvas, element_data["name"])
                element.load_from_data(element_data)
                element.create()
                self.elements.append(element)

            except Exception as e:
                print(f"Error loading element: {e}")








    def save_elements(self, file_path, elements_data):
        """Save elements to a serialized file (e.g., JSON format)."""
        try:
            # Ensure the data is in the correct format
            data_to_save = {"elements": elements_data}  # Wrap the data in the 'elements' key
            
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)  # Save the elements data in the correct format
            
            print(f"Data successfully saved to {file_path}")
        except TypeError:
            print("Error: The elements data is not serializable.")




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hydraulic Transient Simulation")
    project_folder = "C:/Users/Aniket/Desktop/SIH Software/Airavata_Project"  # Define your project folder here
    whiteboard = Whiteboard(root, project_folder)
    whiteboard.pack(fill=tk.BOTH, expand=True)

    # Adding file menu
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open File", command=whiteboard.open_file)
    file_menu.add_command(label="Save File", command=whiteboard.save_file)
    file_menu.add_command(label="Terminate File", command=whiteboard.terminate_file)
    file_menu.add_command(label="New File", command=whiteboard.create_new_file)
    menu_bar.add_cascade(label="File", menu=file_menu)

    root.config(menu=menu_bar)
    root.mainloop()
