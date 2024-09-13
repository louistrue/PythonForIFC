import sys
import os
import asyncio
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Optional
import aiohttp
import networkx as nx
import json

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
    QLineEdit,
    QSplitter,
    QCompleter,
    QTreeWidget,
    QTreeWidgetItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
)
from PySide6.QtCore import Qt, QUrl, QPointF, QEvent
from PySide6.QtGui import QPen, QBrush, QColor, QWheelEvent, QIcon, QAction

import qasync


class GraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._zoom = 0
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event: QWheelEvent):
        """
        Implements zooming using the mouse wheel.
        """
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        if self._zoom < -10:
            self._zoom = -10
            return
        if self._zoom > 50:
            self._zoom = 50
            return

        self.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())

        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def drawBackground(self, painter, rect):
        """
        Draws a white background.
        """
        painter.fillRect(rect, Qt.white)


class IFCConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.ifc_file_path = ""
        self.elements = []
        self.connections = []
        self.description_suggestions = []
        self.node_items = {}

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface.
        """
        self.setWindowTitle("IFC Connector")
        self.setGeometry(100, 100, 1200, 800)

        # Apply modern stylesheet
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
            QLineEdit, QPushButton, QTreeWidget, QComboBox {
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

        # Menu actions
        self.create_actions()

        # File operations layout
        file_layout = QHBoxLayout()
        self.open_file_button = QPushButton("Open IFC File", self)
        self.open_file_button.clicked.connect(self.open_ifc_file)
        file_layout.addWidget(self.open_file_button)

        self.export_button = QPushButton("Export IFC File", self)
        self.export_button.clicked.connect(self.export_ifc_file)
        file_layout.addWidget(self.export_button)

        self.save_config_button = QPushButton("Save Config", self)
        self.save_config_button.clicked.connect(self.save_config)
        file_layout.addWidget(self.save_config_button)

        self.load_config_button = QPushButton("Load Config", self)
        self.load_config_button.clicked.connect(self.load_config)
        file_layout.addWidget(self.load_config_button)

        main_layout.addLayout(file_layout)

        # Splitter to divide the list and the graph
        splitter = QSplitter(Qt.Horizontal)

        # Element selection layout
        element_layout = QVBoxLayout()
        self.label_elements = QLabel("Select Elements to Connect:")
        element_layout.addWidget(self.label_elements)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search Elements...")
        self.search_bar.textChanged.connect(self.filter_elements)
        element_layout.addWidget(self.search_bar)

        self.element_tree = QTreeWidget(self)
        self.element_tree.setHeaderHidden(True)
        self.element_tree.itemChanged.connect(self.element_selection_changed)
        element_layout.addWidget(self.element_tree)

        # Description input
        description_layout = QHBoxLayout()
        self.label_description = QLabel("Description:")
        description_layout.addWidget(self.label_description)

        self.description_input = QLineEdit(self)
        self.description_input.installEventFilter(self)
        description_layout.addWidget(self.description_input)

        element_layout.addLayout(description_layout)

        # Connect button
        self.connect_button = QPushButton("Connect Selected Elements", self)
        self.connect_button.clicked.connect(self.connect_selected_elements)
        element_layout.addWidget(self.connect_button)

        # Container widget for elements
        element_container = QWidget()
        element_container.setLayout(element_layout)

        # Graph visualization using QGraphicsView
        self.graph_view = GraphView(self)
        splitter.addWidget(element_container)
        splitter.addWidget(self.graph_view)
        # Set initial sizes
        splitter.setSizes([400, 800])  # Adjust as needed

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize NetworkX graph
        self.G = nx.Graph()

        # Set up description completer
        self.description_completer = QCompleter(self.description_suggestions)
        self.description_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.description_input.setCompleter(self.description_completer)

    def create_actions(self):
        """
        Creates menu actions.
        """
        self.open_action = QAction("&Open IFC File", self)
        self.open_action.triggered.connect(self.open_ifc_file)

        self.export_action = QAction("&Export IFC File", self)
        self.export_action.triggered.connect(self.export_ifc_file)

        self.save_config_action = QAction("&Save Config", self)
        self.save_config_action.triggered.connect(self.save_config)

        self.load_config_action = QAction("&Load Config", self)
        self.load_config_action.triggered.connect(self.load_config)

    def open_ifc_file(self):
        """
        Opens an IFC file and populates the element tree.
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
            self.display_elements(self.elements)
            QMessageBox.information(self, "Success", f"IFC file loaded: {file_name}")
            self.update_graph_view()

    def list_elements(self):
        """
        Retrieves all IfcElement instances from the IFC file.
        """
        return self.ifc_file.by_type("IfcElement")

    def display_elements(self, elements):
        """
        Displays elements in the QTreeWidget with checkboxes and layers.
        """
        self.element_tree.blockSignals(True)  # Prevent signals during update
        self.element_tree.clear()
        for element in elements:
            item_text = f"{element.Name or 'Unnamed'} ({element.GlobalId})"
            item = QTreeWidgetItem()
            item.setText(0, item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.element = element  # Store the element in the item

            # Check for IfcMaterialLayerSet
            material_layers = self.get_material_layers(element)
            if material_layers:
                for layer in material_layers:
                    layer_item = QTreeWidgetItem(item)
                    layer_text = f"{layer.Name or 'Unnamed'}"
                    layer_item.setText(0, layer_text)
                    layer_item.setFlags(layer_item.flags() | Qt.ItemIsUserCheckable)
                    layer_item.setCheckState(0, Qt.Unchecked)
                    layer_item.layer = layer  # Store the layer in the item
            self.element_tree.addTopLevelItem(item)
        self.element_tree.blockSignals(False)

    def get_material_layers(self, element):
        """
        Retrieves material layers for an element.
        """
        material_layers = []
        associations = element.HasAssociations
        if associations:
            for association in associations:
                if association.is_a("IfcRelAssociatesMaterial"):
                    material = association.RelatingMaterial
                    if material and material.is_a("IfcMaterialLayerSetUsage"):
                        material_layer_set = material.ForLayerSet
                        if material_layer_set and material_layer_set.is_a("IfcMaterialLayerSet"):
                            material_layers.extend(material_layer_set.MaterialLayers)
                    elif material and material.is_a("IfcMaterialLayerSet"):
                        material_layers.extend(material.MaterialLayers)
        return material_layers

    def filter_elements(self, text):
        """
        Filters the elements based on the search text.
        """
        # For simplicity, this function currently does not implement filtering in the tree.
        pass

    def element_selection_changed(self, item, column):
        """
        Updates the graph when an element's selection state changes.
        """
        self.update_graph_view()

    def collect_selected_items(self):
        """
        Collects selected elements and layers.
        """
        selected_items = []

        def recurse(item):
            if item.checkState(0) == Qt.Checked:
                if hasattr(item, 'layer'):
                    selected_items.append(('layer', item.layer, item.parent().element))
                elif hasattr(item, 'element'):
                    selected_items.append(('element', item.element))
            for i in range(item.childCount()):
                recurse(item.child(i))

        root = self.element_tree.invisibleRootItem()
        for i in range(root.childCount()):
            recurse(root.child(i))
        return selected_items

    def connect_selected_elements(self):
        """
        Connects the selected elements and layers with the provided description.
        """
        if not self.ifc_file:
            QMessageBox.warning(self, "Error", "No IFC file loaded.")
            return

        selected_items = self.collect_selected_items()

        if len(selected_items) < 2:
            QMessageBox.warning(self, "Error", "Please select at least two items to connect.")
            return

        description = self.description_input.text()

        # Connect each selected item to every other selected item
        for i in range(len(selected_items)):
            for j in range(i + 1, len(selected_items)):
                item1 = selected_items[i]
                item2 = selected_items[j]

                if item1[0] == 'element' and item2[0] == 'element':
                    element1 = item1[1]
                    element2 = item2[1]
                    connect_element(self.ifc_file, element1, element2, description)
                    connection = (element1.GlobalId, element2.GlobalId, description)
                elif item1[0] == 'layer' and item2[0] == 'layer':
                    # For layers, create a custom connection representation
                    layer1 = item1[1]
                    element1 = item1[2]
                    layer2 = item2[1]
                    element2 = item2[2]
                    # Store the connection
                    connection = (
                        (element1.GlobalId, layer1.Name),
                        (element2.GlobalId, layer2.Name),
                        description
                    )
                else:
                    # Mixed element and layer connection
                    QMessageBox.warning(self, "Error", "Cannot connect elements and layers directly.")
                    continue

                if connection not in self.connections:
                    self.connections.append(connection)
        QMessageBox.information(self, "Success", "Items connected successfully!")
        self.update_graph_view()

    def update_graph_view(self):
        """
        Updates the graph visualization using QGraphicsView and QGraphicsScene.
        """
        self.G.clear()
        self.graph_view.scene.clear()
        self.node_items.clear()

        # First, build the list of nodes and edges
        def add_items():
            for i in range(self.element_tree.topLevelItemCount()):
                item = self.element_tree.topLevelItem(i)
                element = item.element
                element_id = element.GlobalId
                element_label = element.Name or "Unnamed"
                checked = item.checkState(0) == Qt.Checked
                self.G.add_node(element_id, label=element_label, checked=checked, type='element')
                # Add layers if any
                for j in range(item.childCount()):
                    layer_item = item.child(j)
                    layer = layer_item.layer
                    layer_label = layer.Name or "Unnamed"
                    layer_checked = layer_item.checkState(0) == Qt.Checked
                    node_id = (element_id, layer_label)
                    self.G.add_node(node_id, label=layer_label, checked=layer_checked, type='layer')
                    # Optionally, connect layer to element
                    self.G.add_edge(element_id, node_id)

        add_items()

        # Add edges from connections
        for connection in self.connections:
            if isinstance(connection[0], tuple):
                # Layer connection
                node1_id = (connection[0][0], connection[0][1])
                node2_id = (connection[1][0], connection[1][1])
            else:
                # Element connection
                node1_id = connection[0]
                node2_id = connection[1]
            description = connection[2]
            if self.G.has_node(node1_id) and self.G.has_node(node2_id):
                self.G.add_edge(node1_id, node2_id, description=description)

        # Position nodes using a layout algorithm
        pos = nx.spring_layout(self.G, k=0.5, iterations=50)

        # Draw edges
        for edge in self.G.edges(data=True):
            node1_id, node2_id, data = edge
            x1, y1 = pos[node1_id]
            x2, y2 = pos[node2_id]
            line = self.graph_view.scene.addLine(
                x1 * 1000,
                y1 * 1000,
                x2 * 1000,
                y2 * 1000,
                QPen(Qt.gray)
            )
            # Optional: Add edge labels if needed

        # Draw nodes
        for node_id, data in self.G.nodes(data=True):
            x, y = pos[node_id]
            checked = data['checked']
            node_type = data['type']
            if checked:
                color = QColor('red')
            elif any(node_id in conn for conn in self.connections):
                color = QColor('lightblue')
            else:
                color = QColor(200, 200, 200, 100)  # Light gray with transparency

            # Draw the node
            ellipse = QGraphicsEllipseItem(-10, -10, 20, 20)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(Qt.black))
            ellipse.setPos(x * 1000, y * 1000)
            self.graph_view.scene.addItem(ellipse)
            self.node_items[node_id] = ellipse

            # Only show labels for selected items
            if data['checked']:
                label = data['label']
                text_item = QGraphicsTextItem(label)
                text_item.setDefaultTextColor(Qt.black)
                text_item.setPos(x * 1000 + 12, y * 1000 - 10)
                self.graph_view.scene.addItem(text_item)

        # Fit the view to the selected and connected items
        self.fit_view_to_items()

    def fit_view_to_items(self):
        """
        Fits the view to the bounding rectangle of selected and connected items.
        """
        items = []
        for node_id, data in self.G.nodes(data=True):
            if data['checked'] or any(node_id in conn for conn in self.connections):
                if node_id in self.node_items:
                    items.append(self.node_items[node_id])

        if items:
            bounding_rect = items[0].sceneBoundingRect()
            for item in items[1:]:
                bounding_rect = bounding_rect.united(item.sceneBoundingRect())
            margin = 50
            bounding_rect.adjust(-margin, -margin, margin, margin)
            self.graph_view.fitInView(bounding_rect, Qt.KeepAspectRatio)
        else:
            # If no items are selected or connected, fit the whole scene
            self.graph_view.fitInView(self.graph_view.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    async def load_predefined_descriptions(self):
        """
        Asynchronously loads predefined descriptions from the bsdd API.
        """
        url = 'https://api.bsdd.buildingsmart.org/api/Property/v4'
        params = {
            'uri': 'https://identifier.buildingsmart.org/uri/LCA/LCA_properties/0.1/prop/ConnectionMethod',
            'includeClasses': 'true',
            'languageCode': 'EN'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        allowed_values = data.get('allowedValues', [])
                        # Initialize the completer and suggestions
                        self.description_input.setPlaceholderText("Enter description...")
                        self.description_suggestions = []
                        for item in allowed_values:
                            description = item.get('value', '')
                            self.description_suggestions.append(description)
                        # Set up the QCompleter
                        if self.description_suggestions:
                            self.description_completer = QCompleter(self.description_suggestions)
                            self.description_completer.setCaseSensitivity(Qt.CaseInsensitive)
                            self.description_input.setCompleter(self.description_completer)
                    else:
                        QMessageBox.warning(
                            self,
                            'Error',
                            f'Failed to load predefined descriptions: {response.status}'
                        )
        except Exception as e:
            QMessageBox.warning(
                self,
                'Error',
                f'An error occurred while loading descriptions: {str(e)}'
            )

    def eventFilter(self, obj, event):
        """
        Shows the completer popup when the description input gains focus.
        """
        if obj == self.description_input and event.type() == QEvent.FocusIn:
            if self.description_completer:
                self.description_completer.complete()
        return super().eventFilter(obj, event)

    def save_config(self):
        """
        Saves the current configuration to a JSON file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Config File", "", "JSON Files (*.json)", options=options
        )
        if file_name:
            config = {
                'connections': self.connections
            }
            with open(file_name, 'w') as f:
                json.dump(config, f)
            QMessageBox.information(self, "Success", f"Config file saved as {file_name}")

    def load_config(self):
        """
        Loads a configuration from a JSON file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Config File", "", "JSON Files (*.json);;All Files (*)", options=options
        )
        if file_name:
            with open(file_name, 'r') as f:
                config = json.load(f)
            self.connections = config.get('connections', [])
            QMessageBox.information(self, "Success", f"Config file loaded: {file_name}")
            self.update_graph_view()

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

    def closeEvent(self, event):
        """
        Overrides the closeEvent.
        """
        # Nullify the ifc_file reference
        self.ifc_file = None
        event.accept()


def connect_element(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
    description: Optional[str] = None,
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
        for rel in getattr(settings["relating_element"], "ConnectedFrom", []):
            if (
                rel.is_a("IfcRelConnectsElements")
                and rel.RelatingElement == settings["related_element"]
            ):
                incompatible_connections.append(rel)

    if hasattr(settings["related_element"], "ConnectedTo"):
        for rel in getattr(settings["related_element"], "ConnectedTo", []):
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
    # Integrate asyncio with the Qt event loop using qasync
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        connector = IFCConnector()
        connector.show()
        # Start the asynchronous tasks after the event loop is set
        loop.create_task(connector.load_predefined_descriptions())
        loop.run_forever()
