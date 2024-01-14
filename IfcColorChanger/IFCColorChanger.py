import ifcopenshell
from ifcopenshell import api
import json
import sys
from PyQt5 import QtWidgets, QtGui, QtCore 
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout, QSplitter
from PyQt5.QtGui import QPainter, QPolygon, QColor, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QPoint
import math

class ColorWheelWidget(QWidget):
    def __init__(self, material_data, parent=None):
        super().__init__(parent)
        self.material_data = material_data  # List of tuples (material_name, color, entity_count)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = event.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2
        num_materials = len(self.material_data)

        for i, (material, color, count) in enumerate(self.material_data):
            angle_start = 360 / num_materials * i
            angle_end = 360 / num_materials * (i + 1)

            # Draw segment
            painter.setBrush(QColor(*color))
            painter.setPen(Qt.NoPen)
            polygon = QPolygon([self._calculate_point(angle_start, radius, center),
                                self._calculate_point(angle_end, radius, center),
                                center])
            painter.drawPolygon(polygon)

            # Label segment
            text = f"{material}\n#: {count}"  
            painter.setPen(QColor(0, 0, 0))
            font = QFont("Arial", 10)
            painter.setFont(font)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            angle_text = (angle_start + angle_end) / 2
            text_pos = self._calculate_point(angle_text, radius / 2, center)
            painter.drawText(text_pos.x() - text_width // 2, text_pos.y() + text_height // 4, text)


    def _calculate_point(self, angle, radius, center):
        radian = math.radians(angle)
        x = int(center.x() + radius * math.cos(radian))
        y = int(center.y() + radius * math.sin(radian))
        return QPoint(x, y)


class IFCColorChanger(QtWidgets.QWidget):
    """
    A tool to change the color of materials in an IFC file based on a mapping provided in a JSON file.
    """
    def __init__(self):
        """
        Initialize the IFCColorChanger widget.
        """
        super().__init__()
        self.ifc_file = None
        self.material_color_map = {}
        self.initUI()
        self.load_color_map_from_json('IfcScripts\IfcColorChanger\MaterialColorMapping.json')

    def load_color_map_from_json(self, json_file_path):
        """
        Load color mappings from a JSON file.
        """
        try:
            with open(json_file_path, 'r') as file:
                material_data = json.load(file)
            self.material_color_map = {item['Material']: item['Color'] for item in material_data}
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to load JSON file: {e}')

    @staticmethod
    def get_color(value):
        """
        Generate an RGB color based on the provided value.
        """
        return [int(255 * (1 - value)), 0, int(255 * value)]

    def initUI(self):
        """
        Initialize the User Interface.
        """
        mainLayout = QVBoxLayout()
        splitter = QSplitter()  # Create a splitter for resizable layout

        self.loadIFCButton = QtWidgets.QPushButton('Load IFC File')
        self.loadIFCButton.clicked.connect(self.load_ifc_file)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setFixedWidth(400)

        self.saveButton = QtWidgets.QPushButton('Save Changes as new IFC')
        self.saveButton.clicked.connect(self.apply_save_changes)
        self.saveButton.setDisabled(True)

        # Color wheel widget
        self.colorWheelWidget = ColorWheelWidget([])
        self.colorWheelWidget.setMinimumHeight(300)  # Ensure visible height

        # Adding table and color wheel to the splitter
        splitter.addWidget(self.tableWidget)
        splitter.addWidget(self.colorWheelWidget)

        # Adding widgets and splitter to the main layout
        mainLayout.addWidget(self.loadIFCButton)
        mainLayout.addWidget(splitter)  # Add splitter to main layout
        mainLayout.addWidget(self.saveButton)

        self.setLayout(mainLayout)
        self.setWindowTitle('IFC Color Changer')
        self.show()
 

    def load_ifc_file(self):
        """
        Load an IFC file using a file dialog and populate the table with materials.
        """
        file_dialog = QtWidgets.QFileDialog()
        ifc_file_path, _ = file_dialog.getOpenFileName(self, 'Open IFC File', '', 'IFC Files (*.ifc)')
        if ifc_file_path:
            try:
                self.ifc_file = ifcopenshell.open(ifc_file_path)
                self.populate_material_table()
                self.saveButton.setEnabled(True)  # Enable the save button here
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to load IFC file: {e}')
        
        # Update color wheel with new data
        self.update_color_wheel()

    def update_color_wheel(self):
        material_counts = self.aggregate_material_counts()
        material_data = []
        for material_name, color in self.material_color_map.items():
            count = material_counts.get(material_name, 0)
            material_data.append((material_name, color, count))
        
        self.colorWheelWidget.material_data = material_data
        self.colorWheelWidget.update()

    def aggregate_material_counts(self):
        material_counts = {}
        for element in self.ifc_file.by_type('IfcBuildingElement'):
            if hasattr(element, 'HasAssociations'):
                for association in element.HasAssociations:
                    if association.is_a('IfcRelAssociatesMaterial'):
                        material_usage = association.RelatingMaterial

                        if material_usage.is_a('IfcMaterial'):
                            material_name = material_usage.Name
                            material_counts[material_name] = material_counts.get(material_name, 0) + 1

                        elif material_usage.is_a('IfcMaterialLayerSetUsage'):
                            layer_set = material_usage.ForLayerSet
                            for layer in layer_set.MaterialLayers:
                                material_name = layer.Material.Name
                                material_counts[material_name] = material_counts.get(material_name, 0) + 1

        return material_counts  



    def populate_material_table(self):
        """
        Populate the table with materials and color swatches, highlighting missing mappings.
        """
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)  # Three columns: Color Swatch/Apply, Material, New Color
        self.tableWidget.setHorizontalHeaderLabels(['', 'Material', 'New Color'])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)  # Material name column
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)  # New Color column

        if not self.ifc_file:
            return

        # Populate table rows
        for material in self.ifc_file.by_type('IfcMaterial'):
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

            # Checkbox for Color Swatch/Apply
            color_checkbox = QtWidgets.QCheckBox()
            self.tableWidget.setCellWidget(row_position, 0, color_checkbox)

            # Material name
            self.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(material.Name))

            # Retrieve and display the RGB color
            color = self.material_color_map.get(material.Name, [255, 255, 255])  # Default to white if not found
            rgb_string = f"RGB({color[0]}, {color[1]}, {color[2]})"
            color_item = QtWidgets.QTableWidgetItem(rgb_string)
            color_item.setBackground(QtGui.QColor(*color))
            self.tableWidget.setItem(row_position, 2, color_item)  # Corrected column index for color

        # Set properties for better readability and appearance
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setStyleSheet("QTableWidget {alternate-background-color: #f0f0f0;}")
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.sortByColumn(1, QtCore.Qt.AscendingOrder)  # Sort by Material Name
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
                
    

        # Adjust the column widths
        self.tableWidget.setColumnWidth(0, 150)  # Material name column
        self.tableWidget.setColumnWidth(1, 150)  # Color value column
        self.tableWidget.setColumnWidth(2, 50)   # Color swatch/apply column


        # Optionally, adjust row heights for better appearance
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHeight(row, 30)  # Set a fixed height for each row

        # Update UI layout for a polished look
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Improve the look and feelof the table
        self.tableWidget.verticalHeader().setVisible(False) # Hide vertical headers
        self.tableWidget.setShowGrid(False) # Hide grid lines for a cleaner look
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows) # Enable row selection
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # Disable editing

        # Set row and column properties for better readability
        self.tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.tableWidget.setAlternatingRowColors(True)

        # Styling for alternating row colors for better readability
        self.tableWidget.setStyleSheet("QTableWidget {alternate-background-color: #f0f0f0;}")

        # Final adjustments for a clean and user-friendly interface
        self.tableWidget.setSortingEnabled(True)  # Enable sorting by column headers
        self.tableWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)  # Sort by the first column (Material Name)

        # Resizing the table to fit the contents
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()


    def get_representation_and_value(self, material_name):
        representations = []
        for element in self.ifc_file.by_type('IfcBuildingElement'):
            if hasattr(element, 'HasAssociations'):
                for association in element.HasAssociations:
                    if association.is_a('IfcRelAssociatesMaterial'):
                        material_usage = association.RelatingMaterial

                        if material_usage.is_a('IfcMaterial'):
                            if material_usage.Name == material_name:
                                representations.append(element.Representation)

                        elif material_usage.is_a('IfcMaterialLayerSetUsage'):
                            layer_set = material_usage.ForLayerSet
                            if any(layer.Material.Name == material_name for layer in layer_set.MaterialLayers):
                                representations.append(element.Representation)

        value = self.determine_color_value(material_name)
        return representations, value


    def determine_color_value(self, material_name):
        # Assuming the color map provides a float value between 0 and 1
        if material_name in self.material_color_map:
            return self.material_color_map[material_name]
        else:
            # Default value if material is not in the color map
            return 1.0  # A default float value, e.g., 1.0

    def assign_color_to_element(self, ifc_file, representation, value):
        # Check if the value is a list (RGB values) or a float
        if isinstance(value, list) and len(value) == 3:
            # Directly use the RGB values as color
            color = [v / 255.0 for v in value]  # Normalize the RGB values
        elif isinstance(value, float):
            # Use get_color to convert the float value to RGB
            color = IFCColorChanger.get_color(value)
        else:
            print(f"Invalid value for color: {value}")
            return  # Optionally handle this situation more gracefully

        # Create a blank style
        style = ifcopenshell.api.run("style.add_style", ifc_file, name="DynamicStyle")

        # Add surface style shading with color
        try:
            ifcopenshell.api.run("style.add_surface_style", ifc_file, style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": {"Name": None, "Red": color[0], "Green": color[1], "Blue": color[2]}})
        except TypeError as e:
            print(f"TypeError in assigning color: {e}")
            return  # Optionally handle this situation more gracefully

        # Assign the style to the element's representation
        ifcopenshell.api.run("style.assign_representation_styles", ifc_file, shape_representation=representation, styles=[style])


    def apply_save_changes(self):
        if not self.ifc_file:
            return

        try:
            for row in range(self.tableWidget.rowCount()):
                color_checkbox = self.tableWidget.cellWidget(row, 2)
                if isinstance(color_checkbox, QtWidgets.QCheckBox) and color_checkbox.isChecked():
                    material_name = self.tableWidget.item(row, 0).text()
                    representations, value = self.get_representation_and_value(material_name)
                    for representation in representations:
                        if representation is not None and value is not None:
                            self.assign_color_to_element(self.ifc_file, representation, value)


            file_dialog = QtWidgets.QFileDialog()
            new_ifc_file_path, _ = file_dialog.getSaveFileName(self, 'Save IFC File', '', 'IFC Files (*.ifc)')
            if new_ifc_file_path:
                self.ifc_file.write(new_ifc_file_path)
                QtWidgets.QMessageBox.information(self, 'Success', 'IFC file saved with new colors.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error applying changes: {e}')

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = IFCColorChanger()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

