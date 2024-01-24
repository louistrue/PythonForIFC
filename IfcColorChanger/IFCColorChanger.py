import ifcopenshell
from ifcopenshell import api
import json
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QMenuBar, 
                             QTableWidget, QCheckBox, QPushButton, QTextBrowser, 
                             QColorDialog, QMessageBox, QFileDialog, QTableWidgetItem)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal

# Thread class for handling file operations
class FileOperationWorker(QThread):
    finished = pyqtSignal(bool, str, object)

    def __init__(self, filepath, operation):
        super().__init__()
        self.filepath = filepath
        self.operation = operation
        self.ifc_file = None

    def run(self):
        # Threaded method to handle file loading and saving
        try:
            if self.operation == 'load':
                # Open the IFC file and load material data
                self.ifc_file = ifcopenshell.open(self.filepath)
                materials = self.load_material_data(self.ifc_file)
                self.finished.emit(True, "Success", self.ifc_file)
            elif self.operation == 'save':
                # Save the IFC file
                self.ifc_file.write(self.filepath)
            self.finished.emit(True, "Success", self.ifc_file)
        except Exception as e:
            self.finished.emit(False, f"Failed: {str(e)}", {})

    def load_material_data(self, ifc_file):
        # Load material data from the IFC file
        materials = {}
        for material in ifc_file.by_type('IfcMaterial'):
            materials[material.id()] = material.Name
        return materials

# Widget for displaying a color wheel
class ColorWheelWidget(QWidget):
    def __init__(self, material_data, parent=None):
        super().__init__(parent)
        self.material_data = sorted(material_data, key=lambda x: x[2], reverse=True)

    def paintEvent(self, event):
        # Custom paint event for drawing the color wheel
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = min(self.width(), self.height()) - 150
        rect = QRect((self.width() - size) // 2, (self.height() - size) // 2, size, size)
        total_entities = sum(count for _, _, count in self.material_data)
        angle_start = 0

        for _, (material, color, count) in enumerate(self.material_data):
            proportion = count / total_entities
            angle_span = 360 * proportion
            painter.setBrush(QColor(*color))
            painter.setPen(Qt.black)
            painter.drawPie(rect, int(angle_start * 16), int(angle_span * 16))
            angle_start += angle_span

# Dialog for displaying application documentation
class DocumentationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # UI setup for the documentation dialog
        self.setWindowTitle("Documentation")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.textBrowser = QTextBrowser(self)
        self.loadDocumentation()
        layout.addWidget(self.textBrowser)
        closeButton = QPushButton("Close", self)
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)

    def loadDocumentation(self):
        # Load documentation from an external HTML file
        try:
            with open('IfcScripts/IfcColorChanger/docs.html', 'r') as file:
                doc_html = file.read()
            self.textBrowser.setHtml(doc_html)
        except Exception as e:
            self.textBrowser.setText(f"Error loading documentation: {e}")

# Main application widget
class IFCColorChanger(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.material_color_map = {}
        self.initUI()
        self.load_color_map_from_json('IfcScripts/IfcColorChanger/MaterialColorMapping.json')
        self.user_selected_colors = {}
        self.resize(950, 600)
        self.setWindowTitle('IFC Color Changer')
        self.load_ifc_file()
        self.show()

    def load_color_map_from_json(self, json_file_path):
        # Load color mappings from a JSON file
        try:
            with open(json_file_path, 'r') as file:
                material_data = json.load(file)
            self.material_color_map = {item['Material']: item['Color'] for item in material_data}
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load JSON file: {e}')

    @staticmethod
    def get_color(value):
        # Convert a numeric value to an RGB color
        return [int(255 * (1 - value)), 0, int(255 * value)]

    def initUI(self):
        # Setup UI components for the application
        self.menuBar = QMenuBar(self)
        fileMenu = self.menuBar.addMenu('&File')
        loadIFCAction = QtWidgets.QAction('&Load IFC File', self)
        loadIFCAction.triggered.connect(self.load_ifc_file)
        fileMenu.addAction(loadIFCAction)
        exportAction = QtWidgets.QAction('&Export Color Mapping', self)
        exportAction.triggered.connect(self.export_color_mapping)
        fileMenu.addAction(exportAction)
        viewDocsAction = QtWidgets.QAction('&View Documentation', self)
        viewDocsAction.triggered.connect(self.view_documentation)
        fileMenu.addAction(viewDocsAction)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(10, 25, 10, 10)
        splitter = QSplitter()
        self.tableWidget = QTableWidget()
        self.tableWidget.setFixedWidth(400)
        self.colorWheelWidget = ColorWheelWidget([])
        self.colorWheelWidget.setMinimumHeight(300)
        splitter.addWidget(self.tableWidget)
        splitter.addWidget(self.colorWheelWidget)
        mainLayout.addWidget(splitter)
        buttonLayout = QHBoxLayout()
        self.saveButton = QPushButton('Save Changes as new IFC')
        self.saveButton.clicked.connect(self.apply_save_changes)
        self.saveButton.setDisabled(True)
        self.saveButton.setStyleSheet("QPushButton {"
                                      "background-color: #4CAF50; "
                                      "color: white; "
                                      "font-size: 16px; "
                                      "border-radius: 5px; "
                                      "padding: 10px; "
                                      "margin: 10px; "
                                      "}")
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addStretch(1)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.setWindowTitle('IFC Color Changer')
        self.show()

    def view_documentation(self):
        # Method to open the documentation dialog
        dialog = DocumentationDialog(self)
        dialog.exec_()

    def export_color_mapping(self):
        # Method to export color mappings to a JSON file
        combined_color_map = {**self.material_color_map, **self.user_selected_colors}
        json_data = [{"Material": material, "Color": color} for material, color in combined_color_map.items()]
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Color Mapping", "", "JSON Files (*.json)")
        if fileName:
            try:
                with open(fileName, 'w') as file:
                    json.dump(json_data, file, indent=4)
                QMessageBox.information(self, 'Success', 'Color mapping exported successfully.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to export color mapping: {e}')

    def load_ifc_file(self):
        # Method to load an IFC file
        file_dialog = QFileDialog()
        ifc_file_path, _ = file_dialog.getOpenFileName(self, 'Open IFC File', '', 'IFC Files (*.ifc)')
        if ifc_file_path:
            self.worker = FileOperationWorker(ifc_file_path, 'load')
            self.worker.finished.connect(self.on_file_loaded)
            self.worker.start()

    def on_file_loaded(self, success, message, ifc_file):
        # Callback method for when file loading is completed
        if success:
            self.ifc_file = ifc_file
            self.populate_material_table()
            self.update_color_wheel()
            self.saveButton.setEnabled(True)
        else:
            QMessageBox.critical(self, 'Error', message)

    def update_color_wheel(self):
        # Method to update the color wheel with material data
        material_data = [(self.tableWidget.item(row, 1).text(),
                          self.material_color_map.get(self.tableWidget.item(row, 1).text(), [255, 255, 255]),
                          int(self.tableWidget.item(row, 2).text()))
                         for row in range(self.tableWidget.rowCount())]
        material_data.sort(key=lambda x: x[2], reverse=True)
        self.colorWheelWidget.material_data = material_data
        self.colorWheelWidget.update()

    def aggregate_material_counts(self):
        # Method to aggregate counts of materials in the IFC file
        material_counts = {}
        for element in self.ifc_file.by_type('IfcBuildingElement'):
            for association in getattr(element, 'HasAssociations', []):
                if association.is_a('IfcRelAssociatesMaterial'):
                    material_usage = association.RelatingMaterial
                    if material_usage.is_a('IfcMaterial'):
                        material_counts[material_usage.Name] = material_counts.get(material_usage.Name, 0) + 1
                    elif material_usage.is_a('IfcMaterialLayerSetUsage'):
                        for layer in material_usage.ForLayerSet.MaterialLayers:
                            material_counts[layer.Material.Name] = material_counts.get(layer.Material.Name, 0) + 1
        return material_counts  

    def populate_material_table(self):
        # Method to populate the material table with data
        self.tableWidget.setUpdatesEnabled(False)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['', 'Material', 'Count', 'New Color'])
        material_counts = self.aggregate_material_counts()
        for material in sorted(material_counts, key=material_counts.get, reverse=True):
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setCellWidget(row_position, 0, QCheckBox())
            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(material))
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(material_counts[material])))
            if material in self.material_color_map:
                color_item = QTableWidgetItem(f"RGB({*self.material_color_map[material],})")
                color_item.setBackground(QColor(*self.material_color_map[material]))
                self.tableWidget.setItem(row_position, 3, color_item)
            else:
                color_btn = QPushButton('Choose Color')
                color_btn.clicked.connect(lambda _, row=row_position: self.open_color_picker(row))
                self.tableWidget.setCellWidget(row_position, 3, color_btn)
        for column in range(self.tableWidget.columnCount()):
            self.tableWidget.resizeColumnToContents(column)
        self.tableWidget.setMinimumWidth(sum(self.tableWidget.columnWidth(column) for column in range(self.tableWidget.columnCount())) + 60)
        self.tableWidget.setUpdatesEnabled(True)

    def open_color_picker(self, row):
        # Method to let user pick color
        color_dialog = QColorDialog(self)
        if color_dialog.exec_():
            chosen_color = color_dialog.currentColor()
            rgb_values = (chosen_color.red(), chosen_color.green(), chosen_color.blue())
            material_name = self.tableWidget.item(row, 1).text()
            self.user_selected_colors[material_name] = rgb_values
            color_item = QTableWidgetItem(f"RGB({rgb_values[0]}, {rgb_values[1]}, {rgb_values[2]})")
            color_item.setBackground(chosen_color)
            self.tableWidget.setItem(row, 2, color_item)

    def get_representation_and_value(self, material_name):
        # Method to get Representation in ifc
        representations = [element.Representation for element in self.ifc_file.by_type('IfcBuildingElement') 
                           for association in getattr(element, 'HasAssociations', []) 
                           if association.is_a('IfcRelAssociatesMaterial') and (
                               (association.RelatingMaterial.is_a('IfcMaterial') and association.RelatingMaterial.Name == material_name) or 
                               (association.RelatingMaterial.is_a('IfcMaterialLayerSetUsage') and 
                                any(layer.Material.Name == material_name for layer in association.RelatingMaterial.ForLayerSet.MaterialLayers)))]
        return representations, self.determine_color_value(material_name)

    def determine_color_value(self, material_name):
        return self.material_color_map.get(material_name, 1.0)

    def assign_color_to_element(self, ifc_file, representation, value):
        color = [v / 255.0 for v in value] if all(isinstance(v, int) and 0 <= v <= 255 for v in value) else value
        style = ifcopenshell.api.run("style.add_style", ifc_file, name="DynamicStyle")
        ifcopenshell.api.run("style.add_surface_style", ifc_file, style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                             "SurfaceColour": {"Name": None, "Red": color[0], "Green": color[1], "Blue": color[2]}})
        ifcopenshell.api.run("style.assign_representation_styles", ifc_file, shape_representation=representation, styles=[style])

    def apply_save_changes(self):
        if not self.ifc_file:
            return
        for row in range(self.tableWidget.rowCount()):
            color_checkbox = self.tableWidget.cellWidget(row, 0)
            if isinstance(color_checkbox, QCheckBox) and color_checkbox.isChecked():
                material_name = self.tableWidget.item(row, 1).text()
                rgb_values = self.user_selected_colors.get(material_name, self.material_color_map.get(material_name))
                if not rgb_values:
                    continue
                representations, _ = self.get_representation_and_value(material_name)
                for representation in representations:
                    if representation is not None:
                        self.assign_color_to_element(self.ifc_file, representation, rgb_values)
        new_ifc_file_path, _ = QFileDialog.getSaveFileName(self, 'Save IFC File', '', 'IFC Files (*.ifc)')
        if new_ifc_file_path:
            self.ifc_file.write(new_ifc_file_path)
            QMessageBox.information(self, 'Success', 'IFC file saved with new colors.')


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = IFCColorChanger()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
