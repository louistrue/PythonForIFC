import sys
import json
import ifcopenshell
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QFileDialog,
    QTreeWidget, QTreeWidgetItem
)


# Global Variables
loaded_ifc_file = None
all_psets_and_properties = {}
changes = []
old_pset_name = None
old_prop_name = None

# Backend Functions
def load_ifc_file(file_path):
    """Load an IFC file and return its properties and psets."""
    global loaded_ifc_file
    loaded_ifc_file = ifcopenshell.open(file_path)
    return extract_properties_and_psets(loaded_ifc_file)


def extract_properties_and_psets(ifc_file):
    """Extract properties and psets from an IFC file."""
    all_properties = {}
    for obj in ifc_file.by_type("IfcPropertySet"):
        pset_name = obj.Name
        properties = {}
        for prop in obj.HasProperties:
            prop_name = prop.Name
            if prop.is_a("IfcPropertySingleValue"):
                prop_value = prop.NominalValue.wrappedValue if prop.NominalValue else None
            else:
                prop_value = "Complex Type"
            properties[prop_name] = prop_value
        all_properties[pset_name] = properties
    return all_properties


def apply_changes(local_changes):
    """Apply changes to properties and psets."""
    # Debug line to print the value of local_changes
    print("Local changes: ", local_changes)
    
    # Check if local_changes is iterable
    if not isinstance(local_changes, (list, tuple)):
        print("Error: local_changes is not iterable.")
        return
    
    global changes
    for change in local_changes:
        old_pset_name, new_pset_name, old_prop_name, new_prop_name = change
        for obj in loaded_ifc_file.by_type("IfcPropertySet"):
            if obj.Name == old_pset_name:
                print(f"Before: {obj.Name}")  # Debug line
                obj.Name = new_pset_name
                print(f"After: {obj.Name}")  # Debug line
                for prop in obj.HasProperties:
                    if old_prop_name and prop.Name == old_prop_name:
                        prop.Name = new_prop_name
    changes = local_changes
    rename_button.setDisabled(True)


def reset_ui():
    """Reset the UI to its initial state."""
    rename_button.setEnabled(True)


def load_and_populate():
    """Load an IFC file and populate the tree with its properties and psets."""
    global all_psets_and_properties, changes  # Declare them as global to modify
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Load IFC File", "", "IFC Files (*.ifc);;All Files (*)", options=options)
    if file_path:
        all_psets_and_properties = load_ifc_file(file_path)
        changes = []  # Reset changes
        preview_window.clear()  # Clear preview window
        populate_tree()
        reset_ui()

def on_tree_item_clicked(item, column):
    global old_pset_name, old_prop_name
    parent = item.parent()
    
    if parent:  # This is a property item
        old_prop_name = item.text(0).split(" : ")[0]
        old_pset_name = parent.text(0)
    else:  # This is a pset item
        old_pset_name = item.text(0)
        old_prop_name = None

def populate_tree():
    """Populate the tree widget with psets and properties."""
    pset_tree.clear()
    for pset, props in all_psets_and_properties.items():
        pset_item = QTreeWidgetItem(pset_tree)
        pset_item.setText(0, pset)
        for prop, value in props.items():
            prop_item = QTreeWidgetItem(pset_item)
            prop_item.setText(0, f"{prop} : {value}")

def update_changes_and_preview():
    """Update changes and refresh the preview."""
    new_pset_name = text_input.text()
    new_prop_name = None  # Update this as needed
    
    # Update changes
    global changes
    changes.append((old_pset_name, new_pset_name, old_prop_name, new_prop_name))
    
    # Update preview
    preview_window.clear()
    for old_pset, new_pset, old_prop, new_prop in changes:
        if old_prop:  # This is a property
            preview_window.addItem(f"Renamed Property: {old_prop} -> {new_prop}")
        else:  # This is a pset
            preview_window.addItem(f"Renamed Pset: {old_pset} -> {new_pset}")
    print(f"Changes list updated: {changes}")


def save_configurations():
    """Save changes to a JSON file."""
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        window, "Save Configurations", "", "JSON Files (*.json);;All Files (*)", options=options)
    if file_path:
        if not file_path.endswith('.json'):
            file_path += '.json'
        with open(file_path, 'w') as f:
            json.dump(changes, f)

def load_configurations():
    """Load changes from a JSON file."""
    global changes  # Declare 'changes' as global to modify it
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Load Configurations", "", "JSON Files (*.json);;All Files (*)", options=options)
    if file_path:
        with open(file_path, 'r') as f:
            changes = json.load(f)  # Update the global 'changes' variable

        preview_window.clear()  # Clear the existing preview list
        for old_pset_name, new_pset_name, old_prop_name, new_prop_name in changes:
            if old_prop_name:  # This is a property
                preview_window.addItem(f"Renamed Property: {old_prop_name} -> {new_prop_name}")
            else:  # This is a pset
                preview_window.addItem(f"Renamed Pset: {old_pset_name} -> {new_pset_name}")

        apply_changes(changes)  # Apply the loaded changes

def save_ifc_file():
    """Save all changes into a new IFC file."""
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        window, "Save New IFC File", "", "IFC Files (*.ifc);;All Files (*)", options=options)
    if file_path:
        if not file_path.endswith('.ifc'):
            file_path += '.ifc'
        
        # Apply changes before saving
        apply_changes(changes)
        
        loaded_ifc_file.write(file_path)
        print(f"IFC file successfully saved to {file_path}")



# Initialize the application
app = QApplication(sys.argv)

# Create main window and layouts
window = QWidget()
window.setWindowTitle('IFC Property Renamer')
main_layout = QVBoxLayout()
top_section = QHBoxLayout()
middle_section = QHBoxLayout()
lower_section = QHBoxLayout()
bottom_section = QHBoxLayout()

# UI Elements
load_button = QPushButton('Load IFC File')
save_button = QPushButton('Save New IFC File')
pset_tree = QTreeWidget()
preview_window = QListWidget()
text_input = QLineEdit("Enter new name here")
rename_button = QPushButton('Rename')
save_config_button = QPushButton('Save Configurations')
load_config_button = QPushButton('Load Configurations')

# Configure UI Elements
pset_tree.setHeaderLabels(["Psets and Properties"])
preview_window.addItem("Preview List")

# Arrange UI Elements
top_section.addWidget(load_button)
top_section.addWidget(save_button)
middle_section.addWidget(pset_tree)
middle_section.addWidget(preview_window)
lower_section.addWidget(text_input)
lower_section.addWidget(rename_button)
bottom_section.addWidget(save_config_button)
bottom_section.addWidget(load_config_button)

# Add sections to main layout
main_layout.addLayout(top_section)
main_layout.addLayout(middle_section)
main_layout.addLayout(lower_section)
main_layout.addLayout(bottom_section)

# Set layout and show window
window.setLayout(main_layout)
window.show()

# Connect signals and slots
load_button.clicked.connect(load_and_populate)
save_config_button.clicked.connect(save_configurations)
load_config_button.clicked.connect(load_configurations)
save_button.clicked.connect(save_ifc_file)
pset_tree.itemClicked.connect(on_tree_item_clicked)
rename_button.clicked.connect(update_changes_and_preview)


# Run the application
sys.exit(app.exec_())