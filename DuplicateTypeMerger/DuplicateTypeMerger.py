from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
import ifcopenshell
import sys

# Initialize the IFC file variable
ifc_file = None

# Function to load the IFC file
def load_ifc_file():
    global ifc_file
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(None, "Open IFC File", "", "IFC Files (*.ifc);;All Files (*)", options=options)
    if filePath:
        ifc_file = ifcopenshell.open(filePath)
        update_class_list()

# Function to save the IFC file
def save_as_function():
    global ifc_file
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getSaveFileName(None, "Save As", "", "IFC Files (*.ifc);;All Files (*)", options=options)
    if filePath:
        ifc_file.write(filePath)

# Function to convert a given entity to IfcVirtualElement
def convert_entity_to_virtual_element(entity):
    global ifc_file
    virtual_element = ifc_file.createEntity(
        "IfcVirtualElement",
        *[
            entity.get_info()[attribute_name]
            for attribute_name in [
                "GlobalId",
                "OwnerHistory",
                "Name",
                "Description",
                "ObjectType",
            ]
        ],
    )
    ifc_file.remove(entity)
    return virtual_element

# Function to convert selected items to IfcVirtualElement
def convert_to_virtual_element():
    global ifc_file
    selected_items = list_widget.selectedItems()
    if not selected_items:
        return

    selected_class = selected_items[0].text().split(" ")[0]

    for entity in ifc_file.by_type(selected_class):
        convert_entity_to_virtual_element(entity)

    update_class_list()

# Function to update the list of IFC classes
def update_class_list():
    global ifc_file
    if ifc_file is None:
        return

    classes = {}
    for entity in ifc_file:
        ifc_class = entity.is_a()
        classes[ifc_class] = classes.get(ifc_class, 0) + 1

    list_widget.clear()
    for ifc_class, count in classes.items():
        item = QListWidgetItem(f"{ifc_class} ({count})")
        list_widget.addItem(item)

# Initialize the PyQt5 application
app = QApplication([])

# Create the main window and layout
window = QWidget()
layout = QVBoxLayout()

# Create and add widgets to the layout
load_button = QPushButton("Load IFC File")
load_button.clicked.connect(load_ifc_file)
layout.addWidget(load_button)

list_widget = QListWidget()
layout.addWidget(list_widget)

convert_button = QPushButton("Convert to Virtual Element")
convert_button.clicked.connect(convert_to_virtual_element)
layout.addWidget(convert_button)

save_as_button = QPushButton("Save As")
save_as_button.clicked.connect(save_as_function)
layout.addWidget(save_as_button)

# Set up the main window
window.setLayout(layout)
window.setWindowTitle("VirtualElementConverter")
window.show()

sys.exit(app.exec_())