import ifcopenshell
from ifcopenshell import api
import json
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QMenuBar, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QColorDialog, QFileDialog
from PyQt5.QtGui import QPainter, QPolygon, QColor, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5 import QtWidgets, QtCore
import math


class ColorWheelWidget(QWidget):
    def __init__(self, material_data, parent=None):
        super().__init__(parent)
        self.material_data = sorted(
            [(m, c, e) for m, c, e in material_data if e > 0], 
            key=lambda x: x[2], reverse=True
        )
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Adjust size for external labels
        size = min(self.width(), self.height()) - 150  # Reserve space for labels
        rect = QRect(int((self.width() - size) / 2), int((self.height() - size) / 2), size, size)
        center = rect.center()
        radius = size / 2

        total_entities = sum(count for _, _, count in self.material_data)
        angle_start = 0
        for index, (material, color, count) in enumerate(self.material_data):
            if count > 0:
                proportion = count / total_entities
                angle_span = 360 * proportion
                # Draw segment
                painter.setBrush(QColor(*color))
                painter.setPen(Qt.black)  # Set pen to black color
                painter.drawPie(rect, int(angle_start * 16), int(angle_span * 16))
                angle_start += angle_span




class DocumentationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Documentation")
        self.resize(600, 400)  # Adjust the size as needed

        layout = QtWidgets.QVBoxLayout(self)

        # Create a QTextBrowser to display the documentation
        self.textBrowser = QtWidgets.QTextBrowser(self)
        doc_html = """
        <h1>IFC Color Changer Documentation</h1>

        <p>The IFC Color Changer is a tool designed to modify the color properties of materials in IFC files. It allows users to load IFC files, change material colors, save changes, and export color mappings.</p>

        <h2>Getting Started</h2>
        <ol>
            <li><b>Loading an IFC File</b>:
                <ul>
                    <li>Click on 'Load IFC File' to open and load your IFC file into the application.</li>
                </ul>
            </li>
            <li><b>Viewing Material Colors</b>:
                <ul>
                    <li>The Color Wheel Widget displays the current color settings for each material.</li>
                </ul>
            </li>
        </ol>

        <h2>Changing Colors</h2>
        <ul>
            <li><b>Select a Material</b>: Click on a material in the table to select it.</li>
            <li><b>Change Color</b>:
                <ul>
                    <li>Click 'Choose Color' to open the color picker.</li>
                    <li>Select a color and confirm your choice.</li>
                </ul>
            </li>
            <li><b>Applying Changes</b>:
                <ul>
                    <li>Once you've chosen new colors, click 'Save Changes as new IFC' to apply the changes to the IFC file.</li>
                </ul>
            </li>
        </ul>

        <h2>Exporting Color Mappings</h2>
        <ul>
            <li>To export your color settings, go to 'More' &gt; 'Export Color Mapping'.</li>
            <li>Choose a location to save the JSON file containing your color mappings.</li>
        </ul>

        <h2>Troubleshooting and Support</h2>
        <p>If you encounter any issues or have questions, please contact our support team at support@example.com.</p>

        <h2>About</h2>
        <ul>
            <li>IFC Color Changer version 1.0</li>
            <li>Developed by Louis Trümpler</li>
        </ul>

        """
        self.textBrowser.setHtml(doc_html)
        layout.addWidget(self.textBrowser)

        # Close button
        closeButton = QtWidgets.QPushButton("Close", self)
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)
        



class IFCColorChanger(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.material_color_map = {}
        self.initUI()
        self.load_color_map_from_json('IfcScripts/IfcColorChanger/2396MaterialColorMapping.json')
        self.user_selected_colors = {}
        self.resize(950, 600)
        self.setWindowTitle('IFC Color Changer')

        # Automatically open the file dialog to load an IFC file
        self.load_ifc_file()

        self.show()

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
        self.menuBar = QMenuBar(self)  
        # Menu Bar
        self.menuBar = QMenuBar(self)
        fileMenu = self.menuBar.addMenu('&File')

        # Load IFC File Action
        loadIFCAction = QtWidgets.QAction('&Load IFC File', self)
        loadIFCAction.triggered.connect(self.load_ifc_file)
        fileMenu.addAction(loadIFCAction)
        exportAction = QtWidgets.QAction('&Export Color Mapping', self)
        exportAction.triggered.connect(self.export_color_mapping)
        fileMenu.addAction(exportAction)
        # Add 'View Documentation' action
        viewDocsAction = QtWidgets.QAction('&View Documentation', self)
        viewDocsAction.triggered.connect(self.view_documentation)
        fileMenu.addAction(viewDocsAction)
        mainLayout = QVBoxLayout()
        # Set top margin for the main layout
        mainLayout.setContentsMargins(10, 25, 10, 10)  # Adjust the second parameter to increase/decrease top margin
        splitter = QSplitter()  # Create a splitter for resizable layout

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setFixedWidth(400)

        # Color wheel widget
        self.colorWheelWidget = ColorWheelWidget([])
        self.colorWheelWidget.setMinimumHeight(300)  # Ensure visible height
        # Adding table and color wheel to the splitter
        splitter.addWidget(self.tableWidget)
        splitter.addWidget(self.colorWheelWidget)
        mainLayout.addWidget(splitter)  # Add splitter to main layout
        # Create a horizontal layout for the save button
        buttonLayout = QHBoxLayout()
        self.saveButton = QtWidgets.QPushButton('Save Changes as new IFC')
        self.saveButton.clicked.connect(self.apply_save_changes)
        self.saveButton.setDisabled(True)

        # Style the save button
        self.saveButton.setStyleSheet("QPushButton {"
                                      "background-color: #4CAF50; "  # Example green color
                                      "color: white; "
                                      "font-size: 16px; "
                                      "border-radius: 5px; "
                                      "padding: 10px; "
                                      "margin: 10px; "
                                      "}")
        # Adding stretch to center the button
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addStretch(1)

        # Add the buttonLayout to the mainLayout
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.setWindowTitle('IFC Color Changer')
        self.show()

        # Set the button width after the UI is shown
        app_width = self.width()
        button_width = int(2/3 * app_width)
        self.saveButton.setFixedWidth(button_width)


        buttonLayout.addWidget(self.saveButton)



        # Add the buttonLayout to the mainLayout
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.setWindowTitle('IFC Color Changer')
        self.show()

    def view_documentation(self):
        dialog = DocumentationDialog(self)
        dialog.exec_()


    def export_color_mapping(self):
        # Combine both predefined and user-defined color mappings
        combined_color_map = {**self.material_color_map, **self.user_selected_colors}

        # Transform the color mapping into the required JSON structure
        json_data = [{"Material": material, "Color": color} for material, color in combined_color_map.items()]

        # Ask the user where to save the JSON file
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Color Mapping", "", "JSON Files (*.json)", options=options)

        if fileName:
            try:
                with open(fileName, 'w') as file:
                    json.dump(json_data, file, indent=4)
                QtWidgets.QMessageBox.information(self, 'Success', 'Color mapping exported successfully.')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to export color mapping: {e}')



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
        # Initialize an empty list for material_data
        material_data = []

        # Iterate over the rows of the table
        for row in range(self.tableWidget.rowCount()):
            material_name = self.tableWidget.item(row, 1).text()
            color = self.material_color_map.get(material_name, [255, 255, 255])  # Default to white if not found
            count = int(self.tableWidget.item(row, 2).text())
            material_data.append((material_name, color, count))

        # Sort material_data by count in the same way as the table
        material_data.sort(key=lambda x: x[2], reverse=True)

        # Update the material_data in the color wheel
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
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['', 'Material', 'Count', 'New Color'])

        if not self.ifc_file:
            return

        material_counts = self.aggregate_material_counts()

        # Sort materials by count
        sorted_materials = sorted(self.ifc_file.by_type('IfcMaterial'), key=lambda m: material_counts.get(m.Name, 0), reverse=True)

        for material in sorted_materials:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

            # Checkbox for Color Swatch/Apply
            color_checkbox = QtWidgets.QCheckBox()
            self.tableWidget.setCellWidget(row_position, 0, color_checkbox)

            # Material name
            self.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(material.Name))

            # Material count
            count = material_counts.get(material.Name, 0)
            count_item = QtWidgets.QTableWidgetItem(str(count))
            self.tableWidget.setItem(row_position, 2, count_item)

            # Color chooser or display
            if material.Name in self.material_color_map:
                color_checkbox.setChecked(True)
                color = self.material_color_map[material.Name]
                rgb_string = f"RGB({color[0]}, {color[1]}, {color[2]})"
                color_item = QtWidgets.QTableWidgetItem(rgb_string)
                color_item.setBackground(QtGui.QColor(*color))
                self.tableWidget.setItem(row_position, 3, color_item)
            else:
                color_btn = QtWidgets.QPushButton('Choose Color')
                color_btn.clicked.connect(lambda _, row=row_position: self.open_color_picker(row))
                self.tableWidget.setCellWidget(row_position, 3, color_btn)



        # Resize each column to fit its contents
        for column in range(self.tableWidget.columnCount()):
            self.tableWidget.resizeColumnToContents(column)

        # Optionally, set a minimum width for the table
        total_width = sum([self.tableWidget.columnWidth(column) for column in range(self.tableWidget.columnCount())])
        self.tableWidget.setMinimumWidth(total_width + 60) 

    def open_color_picker(self, row):
        color_dialog = QtWidgets.QColorDialog(self)
        if color_dialog.exec_():
            chosen_color = color_dialog.currentColor()
            rgb_values = (chosen_color.red(), chosen_color.green(), chosen_color.blue())
            rgb_string = f"RGB({rgb_values[0]}, {rgb_values[1]}, {rgb_values[2]})"

            # Store the RGB values in the user-selected colors dictionary
            material_name = self.tableWidget.item(row, 1).text()
            self.user_selected_colors[material_name] = rgb_values

            color_item = QtWidgets.QTableWidgetItem(rgb_string)
            color_item.setBackground(chosen_color)
            self.tableWidget.setItem(row, 2, color_item)




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
        # Check if the value is a list (RGB values)
        if isinstance(value, tuple) or isinstance(value, list):
            # Normalize the RGB values if they are in standard 0-255 range
            if all(isinstance(v, int) and 0 <= v <= 255 for v in value):
                color = [v / 255.0 for v in value]
            else:
                # Handle the case where the RGB values are already normalized or incorrect
                color = value
        elif isinstance(value, float):
            # Use get_color to convert the float value to RGB
            color = IFCColorChanger.get_color(value)
        else:
            print(f"Invalid value for color: {value}")
            return  

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
                color_checkbox = self.tableWidget.cellWidget(row, 0)
                if isinstance(color_checkbox, QtWidgets.QCheckBox) and color_checkbox.isChecked():
                    material_name = self.tableWidget.item(row, 1).text()

                    # Check if the color is user-selected or from JSON mapping
                    if material_name in self.user_selected_colors:
                        # User-selected color
                        rgb_values = self.user_selected_colors[material_name]
                    elif material_name in self.material_color_map:
                        # Color from JSON mapping
                        rgb_values = self.material_color_map[material_name]
                    else:
                        # Skip if no color is selected
                        continue

                    # Get representations for the material
                    representations, _ = self.get_representation_and_value(material_name)
                    for representation in representations:
                        if representation is not None:
                            # Apply the color to the element
                            self.assign_color_to_element(self.ifc_file, representation, rgb_values)


            # Save the modified IFC file
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

