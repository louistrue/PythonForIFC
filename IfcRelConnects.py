import sys
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QComboBox, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from typing import Optional
import os
import asyncio
import aiohttp
import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def quote_if_colon(s):
    if isinstance(s, str) and ':' in s:
        return f'"{s}"'
    return s

class IFCConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.connections = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('IFC Element Connector')
        self.setGeometry(100, 100, 1000, 800)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
                color: #212121;
            }
            QLabel {
                color: #212121;
            }
            QLineEdit, QComboBox, QPushButton {
                background-color: #FFFFFF;
                color: #212121;
                border: 1px solid #BDBDBD;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                selection-background-color: #E0E0E0;
                color: #212121;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #BDBDBD;
            }
            QLineEdit:focus, QComboBox:focus, QPushButton:focus {
                border: 1px solid #1E88E5;
            }
        """)

        main_layout = QVBoxLayout()

        # Open file button
        open_file_layout = QHBoxLayout()
        self.open_file_button = QPushButton('Open IFC File', self)
        self.open_file_button.clicked.connect(self.open_ifc_file)
        open_file_layout.addWidget(self.open_file_button)
        main_layout.addLayout(open_file_layout)

        # Element selection layout
        element_layout = QVBoxLayout()

        self.label1 = QLabel('Select Relating Element:')
        element_layout.addWidget(self.label1)

        self.combo1 = QComboBox(self)
        element_layout.addWidget(self.combo1)

        self.label2 = QLabel('Select Related Element:')
        element_layout.addWidget(self.label2)

        self.combo2 = QComboBox(self)
        element_layout.addWidget(self.combo2)

        main_layout.addLayout(element_layout)

        # Description input layout
        description_layout = QVBoxLayout()
        
        description_input_layout = QHBoxLayout()
        self.label3 = QLabel('Description:')
        description_input_layout.addWidget(self.label3)

        self.description_input = QComboBox(self)
        self.description_input.setEditable(True)
        description_input_layout.addWidget(self.description_input)

        description_layout.addLayout(description_input_layout)

        main_layout.addLayout(description_layout)

        # Buttons layout
        button_layout = QHBoxLayout()

        self.connect_button = QPushButton('Connect Elements', self)
        self.connect_button.clicked.connect(self.connect_elements)
        button_layout.addWidget(self.connect_button)

        self.save_button = QPushButton('Save IFC File', self)
        self.save_button.clicked.connect(self.save_ifc_file)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

        # Graph view for connections
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        asyncio.run(self.load_predefined_descriptions())

    def open_ifc_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open IFC File", "", "IFC Files (*.ifc);;All Files (*)", options=options)
        if file_name:
            self.ifc_file_path = file_name
            self.ifc_file = ifcopenshell.open(file_name)
            self.combo1.clear()
            self.combo2.clear()
            elements = [f"{element.Name} ({element.GlobalId})" for element in self.list_elements()]
            self.combo1.addItems(elements)
            self.combo2.addItems(elements)
            QMessageBox.information(self, 'Success', f'IFC file loaded: {file_name}')
            self.update_graph_view()

    def list_elements(self):
        return self.ifc_file.by_type("IfcElement")

    def connect_elements(self):
        if not self.ifc_file:
            QMessageBox.warning(self, 'Error', 'No IFC file loaded.')
            return

        element1_text = self.combo1.currentText()
        element2_text = self.combo2.currentText()

        element1_id = element1_text.split('(')[-1][:-1]
        element2_id = element2_text.split('(')[-1][:-1]

        description = self.description_input.currentText()

        element1 = self.ifc_file.by_guid(element1_id)
        element2 = self.ifc_file.by_guid(element2_id)

        if element1 and element2:
            connect_element(self.ifc_file, element1, element2, description)
            self.connections.append((element1_text, element2_text, description))
            self.update_graph_view()
            QMessageBox.information(self, 'Success', 'Elements connected successfully!')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to connect elements.')

    def save_ifc_file(self):
        if not self.ifc_file:
            QMessageBox.warning(self, 'Error', 'No IFC file loaded.')
            return

        directory = os.path.dirname(self.ifc_file_path)
        base_name = os.path.basename(self.ifc_file_path)
        new_file_path = os.path.join(directory, f"modified_{base_name}")

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save IFC File", new_file_path, "IFC Files (*.ifc)", options=options)
        if file_name:
            self.ifc_file.write(file_name)
            QMessageBox.information(self, 'Success', f'IFC file saved as {file_name}')

    async def load_predefined_descriptions(self):
        url = 'https://api.bsdd.buildingsmart.org/api/Property/v4'
        params = {
            'uri': 'https://identifier.buildingsmart.org/uri/LCA/LCA_properties/0.1/prop/ConnectionMethod',
            'includeClasses': 'true',
            'languageCode': 'EN'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('allowedValues', []):
                        self.description_input.addItem(item['value'])
                else:
                    QMessageBox.warning(self, 'Error', f'Failed to load predefined descriptions: {response.status}')

    def update_graph_view(self):
        self.figure.clear()
        G = nx.DiGraph()

        element_positions = {}

        # Only add nodes and edges for connected elements
        for connection in self.connections:
            element1_text, element2_text, description = connection
            element1_id = element1_text.split('(')[-1][:-1]
            element2_id = element2_text.split('(')[-1][:-1]

            element1 = self.ifc_file.by_guid(element1_id)
            element2 = self.ifc_file.by_guid(element2_id)

            if element1 and element2:
                node_label1 = quote_if_colon(f"{element1.Name} ({element1.GlobalId})")
                node_label2 = quote_if_colon(f"{element2.Name} ({element2.GlobalId})")
                
                G.add_node(element1.GlobalId, label=node_label1)
                G.add_node(element2.GlobalId, label=node_label2)
                G.add_edge(element1_id, element2_id, label=quote_if_colon(description))

        pos = graphviz_layout(G, prog='dot')

        nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_size=3000, node_color='skyblue', font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        self.canvas.draw()


def connect_element(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
    description: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    settings = {
        "relating_element": relating_element,
        "related_element": related_element,
        "description": description,
    }

    incompatible_connections = []

    for rel in settings["relating_element"].ConnectedFrom:
        if rel.is_a("IfcRelConnectsElements") and rel.RelatingElement == settings["related_element"]:
            incompatible_connections.append(rel)

    for rel in settings["related_element"].ConnectedTo:
        if rel.is_a("IfcRelConnectsElements") and rel.RelatedElement == settings["relating_element"]:
            incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    for rel in settings["relating_element"].ConnectedTo:
        if rel.is_a("IfcRelConnectsElements") and rel.RelatedElement == settings["related_element"]:
            rel.Description = settings["description"]
            return rel

    # Reuse existing OwnerHistory
    owner_history = relating_element.OwnerHistory

    return file.createIfcRelConnectsElements(
        ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        Description=settings["description"],
        RelatingElement=settings["relating_element"],
        RelatedElement=settings["related_element"],
    )

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    connector = IFCConnector()
    connector.show()
    sys.exit(app.exec_())
