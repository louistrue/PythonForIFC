import sys
import os
import json
import asyncio
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QAbstractItemView,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon

# Ensure that PySide6-WebEngine is installed
from PySide6.QtWebEngineWidgets import QWebEngineView

import aiohttp
import networkx as nx
from pyvis.network import Network


class IFCConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.ifc_file_path = ""
        self.elements = []
        self.connections = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("IFC Connector")
        self.setGeometry(100, 100, 1200, 800)

        # Set a modern stylesheet for the application
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 14px;
            }
            QLineEdit, QPushButton, QListWidget {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #555;
            }
            QLineEdit:focus, QPushButton:focus {
                border: 1px solid #1E88E5;
            }
            """
        )

        # Main layout
        main_layout = QVBoxLayout()

        # File operations layout
        file_layout = QHBoxLayout()
        self.open_file_button = QPushButton("Open IFC File", self)
        self.open_file_button.clicked.connect(self.open_ifc_file)
        file_layout.addWidget(self.open_file_button)

        self.export_button = QPushButton("Export IFC File", self)
        self.export_button.clicked.connect(self.export_ifc_file)
        file_layout.addWidget(self.export_button)

        self.save_settings_button = QPushButton("Save Settings", self)
        self.save_settings_button.clicked.connect(self.save_settings)
        file_layout.addWidget(self.save_settings_button)

        self.load_settings_button = QPushButton("Load Settings", self)
        self.load_settings_button.clicked.connect(self.load_settings)
        file_layout.addWidget(self.load_settings_button)

        main_layout.addLayout(file_layout)

        # Element selection layout
        selection_layout = QHBoxLayout()

        # Left side (Relating Elements)
        left_layout = QVBoxLayout()
        self.label1 = QLabel("Select Relating Elements:")
        left_layout.addWidget(self.label1)

        self.search1 = QLineEdit(self)
        self.search1.setPlaceholderText("Search Relating Elements...")
        self.search1.textChanged.connect(self.filter_elements1)
        left_layout.addWidget(self.search1)

        self.list1 = QListWidget(self)
        self.list1.setSelectionMode(QAbstractItemView.MultiSelection)
        left_layout.addWidget(self.list1)

        selection_layout.addLayout(left_layout)

        # Right side (Related Elements)
        right_layout = QVBoxLayout()
        self.label2 = QLabel("Select Related Elements:")
        right_layout.addWidget(self.label2)

        self.search2 = QLineEdit(self)
        self.search2.setPlaceholderText("Search Related Elements...")
        self.search2.textChanged.connect(self.filter_elements2)
        right_layout.addWidget(self.search2)

        self.list2 = QListWidget(self)
        self.list2.setSelectionMode(QAbstractItemView.MultiSelection)
        right_layout.addWidget(self.list2)

        selection_layout.addLayout(right_layout)

        main_layout.addLayout(selection_layout)

        # Description input layout
        description_layout = QHBoxLayout()
        self.label3 = QLabel("Description:")
        description_layout.addWidget(self.label3)

        self.description_input = QLineEdit(self)
        description_layout.addWidget(self.description_input)

        main_layout.addLayout(description_layout)

        # Connect button
        self.connect_button = QPushButton("Connect Elements", self)
        self.connect_button.clicked.connect(self.connect_items)
        main_layout.addWidget(self.connect_button)

        # Graph visualization
        self.web_view = QWebEngineView(self)
        main_layout.addWidget(self.web_view)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Asynchronously load predefined descriptions
        asyncio.ensure_future(self.load_predefined_descriptions())

    def open_ifc_file(self):
        """
        Opens an IFC file and populates the element lists.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open IFC File",
            "",
            "IFC Files (*.ifc);;All Files (*)",
            options=options,
        )
        if file_name:
            self.ifc_file_path = file_name
            self.ifc_file = ifcopenshell.open(file_name)
            self.elements = [element for element in self.list_elements()]
            self.display_elements(self.list1, self.elements)
            self.display_elements(self.list2, self.elements)
            QMessageBox.information(self, "Success", f"IFC file loaded: {file_name}")
            self.update_graph_view()

    def list_elements(self):
        """
        Retrieves all IfcElement instances from the IFC file.
        """
        return self.ifc_file.by_type("IfcElement")

    def display_elements(self, list_widget, elements):
        """
        Displays elements in the given QListWidget.
        """
        list_widget.clear()
        for element in elements:
            item_text = f"{element.Name or 'Unnamed'} ({element.GlobalId})"
            list_widget.addItem(item_text)

    def filter_elements1(self, text):
        """
        Filters the relating elements based on the search text.
        """
        filtered_elements = [
            e
            for e in self.elements
            if text.lower() in (e.Name or "").lower() or text.lower() in e.GlobalId.lower()
        ]
        self.display_elements(self.list1, filtered_elements)

    def filter_elements2(self, text):
        """
        Filters the related elements based on the search text.
        """
        filtered_elements = [
            e
            for e in self.elements
            if text.lower() in (e.Name or "").lower() or text.lower() in e.GlobalId.lower()
        ]
        self.display_elements(self.list2, filtered_elements)

    def connect_items(self):
        """
        Connects selected items with the provided description.
        """
        if not self.ifc_file:
            QMessageBox.warning(self, "Error", "No IFC file loaded.")
            return

        items1 = self.list1.selectedItems()
        items2 = self.list2.selectedItems()

        if not items1 or not items2:
            QMessageBox.warning(self, "Error", "Please select items to connect.")
            return

        description = self.description_input.text()

        for item1 in items1:
            element1_id = item1.text().split("(")[-1][:-1]
            element1 = self.ifc_file.by_guid(element1_id)

            for item2 in items2:
                element2_id = item2.text().split("(")[-1][:-1]
                element2 = self.ifc_file.by_guid(element2_id)

                if element1 and element2:
                    # Connect elements and add to connections list
                    connect_element(self.ifc_file, element1, element2, description)
                    self.connections.append((item1.text(), item2.text(), description))

        self.update_graph_view()
        QMessageBox.information(self, "Success", "Items connected successfully!")

    def update_graph_view(self):
        """
        Updates the graph visualization using PyVis.
        """
        net = Network(height="600px", width="100%", notebook=False)
        net.toggle_physics(True)

        for connection in self.connections:
            item1_text, item2_text, description = connection
            net.add_node(item1_text, label=item1_text)
            net.add_node(item2_text, label=item2_text)
            net.add_edge(item1_text, item2_text, title=description)

        # Save and load the graph in the web view
        net.show("graph.html")
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("graph.html")))

    def export_ifc_file(self):
        """
        Exports the modified IFC file.
        """
        if not self.ifc_file:
            QMessageBox.warning(self, "Error", "No IFC file loaded.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export IFC File", "", "IFC Files (*.ifc)", options=options
        )
        if file_name:
            self.ifc_file.write(file_name)
            QMessageBox.information(self, "Success", f"IFC file exported as {file_name}")

    def save_settings(self):
        """
        Saves the current connections to a JSON file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Settings", "", "JSON Files (*.json)", options=options
        )
        if file_name:
            with open(file_name, "w") as f:
                json.dump(self.connections, f)
            QMessageBox.information(self, "Success", f"Settings saved to {file_name}")

    def load_settings(self):
        """
        Loads connections from a JSON file and applies them to the IFC file.
        """
        if not self.ifc_file:
            QMessageBox.warning(self, "Error", "No IFC file loaded.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Settings", "", "JSON Files (*.json)", options=options
        )
        if file_name:
            with open(file_name, "r") as f:
                saved_connections = json.load(f)
            self.connections = []
            for item1_text, item2_text, description in saved_connections:
                element1_id = item1_text.split("(")[-1][:-1]
                element2_id = item2_text.split("(")[-1][:-1]
                element1 = self.ifc_file.by_guid(element1_id)
                element2 = self.ifc_file.by_guid(element2_id)
                if element1 and element2:
                    connect_element(self.ifc_file, element1, element2, description)
                    self.connections.append((item1_text, item2_text, description))
            self.update_graph_view()
            QMessageBox.information(self, "Success", "Settings loaded and applied.")

    async def load_predefined_descriptions(self):
        """
        Asynchronously loads predefined descriptions to aid user input.
        """
        url = "https://api.bsdd.buildingsmart.org/api/Property/v4"
        params = {
            "uri": "https://identifier.buildingsmart.org/uri/LCA/LCA_properties/0.1/prop/ConnectionMethod",
            "includeClasses": "true",
            "languageCode": "EN",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Handle the data if needed
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Failed to load predefined descriptions: {response.status}",
                        )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"An error occurred while loading descriptions: {str(e)}",
            )


def connect_element(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
    description: str = None,
) -> ifcopenshell.entity_instance:
    """
    Creates or updates a connection between two elements in the IFC file.

    Args:
        file: The IFC file instance.
        relating_element: The element that is the source of the connection.
        related_element: The element that is the target of the connection.
        description: An optional description of the connection.

    Returns:
        The created or updated IfcRelConnectsElements instance.
    """
    settings = {
        "relating_element": relating_element,
        "related_element": related_element,
        "description": description,
    }

    # Remove any existing incompatible connections
    incompatible_connections = []

    if hasattr(settings["relating_element"], "ConnectedFrom"):
        for rel in settings["relating_element"].ConnectedFrom:
            if (
                rel.is_a("IfcRelConnectsElements")
                and rel.RelatingElement == settings["related_element"]
            ):
                incompatible_connections.append(rel)

    if hasattr(settings["related_element"], "ConnectedTo"):
        for rel in settings["related_element"].ConnectedTo:
            if (
                rel.is_a("IfcRelConnectsElements")
                and rel.RelatedElement == settings["relating_element"]
            ):
                incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # Update existing connection if it exists
    for rel in getattr(settings["relating_element"], "ConnectedTo", []):
        if (
            rel.is_a("IfcRelConnectsElements")
            and rel.RelatedElement == settings["related_element"]
        ):
            rel.Description = settings["description"]
            return rel

    # Reuse existing OwnerHistory if available
    owner_history = relating_element.OwnerHistory

    # Create a new IfcRelConnectsElements relationship
    return file.createIfcRelConnectsElements(
        ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        Description=settings["description"],
        RelatingElement=settings["relating_element"],
        RelatedElement=settings["related_element"],
    )


if __name__ == "__main__":
    # Initialize the application
    app = QApplication(sys.argv)
    connector = IFCConnector()
    connector.show()

    # Run the application's event loop
    sys.exit(app.exec())
