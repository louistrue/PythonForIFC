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

class IFCConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('IFC Element Connector')
        self.setGeometry(100, 100, 600, 400)

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
        description_layout = QHBoxLayout()
        self.label3 = QLabel('Description:')
        description_layout.addWidget(self.label3)
        
        self.description = QLineEdit(self)
        description_layout.addWidget(self.description)
        
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

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        
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

        description = self.description.text()

        element1 = self.ifc_file.by_guid(element1_id)
        element2 = self.ifc_file.by_guid(element2_id)

        if element1 and element2:
            connect_element(self.ifc_file, element1, element2, description)
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
