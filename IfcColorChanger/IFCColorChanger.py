import ifcopenshell
from ifcopenshell import api
import json
from PyQt5 import QtWidgets, QtGui, QtCore
import sys

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
        layout = QtWidgets.QVBoxLayout()

        self.loadIFCButton = QtWidgets.QPushButton('Load IFC File')
        self.loadIFCButton.clicked.connect(self.load_ifc_file)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Material', 'New Color', 'Apply Change'])

        self.saveButton = QtWidgets.QPushButton('Save Changes as new IFC')
        self.saveButton.clicked.connect(self.apply_save_changes)
        self.saveButton.setDisabled(True)

        layout.addWidget(self.loadIFCButton)
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.saveButton)

        self.setLayout(layout)
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


    def populate_material_table(self):
        """
        Populate the table with materials and color swatches, highlighting missing mappings.
        The color swatch also acts as a checkbox to select materials for applying changes.
        """
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)  # Reduced the column count
        self.tableWidget.setHorizontalHeaderLabels(['Material', 'New Color', 'Color Swatch/Apply'])

        if not self.ifc_file:
            return
        
        

        for material in self.ifc_file.by_type('IfcMaterial'):
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

            material_name = material.Name
            material_item = QtWidgets.QTableWidgetItem(material_name)
            self.tableWidget.setItem(row_position, 0, material_item)

            # Retrieve and display the RGB color
            color = self.material_color_map.get(material_name, [255, 255, 255])  # Default to white if not found
            rgb_string = f"RGB({color[0]}, {color[1]}, {color[2]})"
            color_item = QtWidgets.QTableWidgetItem(rgb_string)
            
            # Set the background color for the RGB cell
            color_item.setBackground(QtGui.QColor(color[0], color[1], color[2]))
            color_item.setForeground(QtGui.QColor(255, 255, 255) if sum(color) < 400 else QtGui.QColor(0, 0, 0))  # Adjust text color for visibility

            self.tableWidget.setItem(row_position, 1, color_item)

            # Create a checkbox for color swatch and applying changes
            color_checkbox = QtWidgets.QCheckBox()
            color_checkbox.setStyleSheet(
                "background-color: rgb({0}, {1}, {2});".format(color[0], color[1], color[2]) +
                "border-radius: 5px;"  # Rounded corners for visual appeal
            )
            color_checkbox.setChecked(True)  # Automatically check the checkbox
            color_checkbox.setFixedSize(40, 20)  # Set a fixed size for the checkbox
            self.tableWidget.setCellWidget(row_position, 2, color_checkbox)


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

