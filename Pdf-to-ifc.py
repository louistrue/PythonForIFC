import ifcopenshell
import fitz  # PyMuPDF
import sys
import json
import math
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from ifcopenshell.util.placement import get_local_placement
from scipy.spatial import KDTree

CONFIG_FILE = "config.json"

def read_ifc_file(ifc_path):
    return ifcopenshell.open(ifc_path)

def read_pdf_file(pdf_path):
    return fitz.open(pdf_path)

def get_element_location(element):
    try:
        placement_matrix = get_local_placement(element.ObjectPlacement)
        x, y, z, _ = placement_matrix[0, 3], placement_matrix[1, 3], placement_matrix[2, 3], placement_matrix[3, 3]
        return (x, y, z)
    except AttributeError:
        return None

def extract_storey_elements(ifc_model, target_storey_name):
    storeys = ifc_model.by_type('IfcBuildingStorey')
    target_storey = next((storey for storey in storeys if storey.Name == target_storey_name), None)
    if not target_storey:
        return [], None

    target_elevation = target_storey.Elevation
    origin = (0, 0, target_elevation)
    elements = [(element, get_element_location(element)) for element in ifc_model.by_type("IfcWall") if get_element_location(element) and abs(get_element_location(element)[2] - target_elevation) < 1e-6]
    return elements, origin

def extract_pdf_markups(pdf_document):
    markups, zero_zero_marker, x_axis_marker, y_axis_marker = [], None, None, None
    for page in pdf_document:
        for annot in page.annots():
            rect = annot.rect
            center = ((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2)
            comment = annot.info.get("content", "") if annot.info else ""
            if "0/0" in comment:
                zero_zero_marker = center
            elif "x axis" in comment:
                x_axis_marker = center
            elif "y axis" in comment:
                y_axis_marker = center
            else:
                markups.append((center, comment))
    return zero_zero_marker, x_axis_marker, y_axis_marker, markups

def calculate_transformations(zero_zero_marker, x_axis_marker, y_axis_marker):
    x_axis_vector = (x_axis_marker[0] - zero_zero_marker[0], x_axis_marker[1] - zero_zero_marker[1])
    y_axis_vector = (y_axis_marker[0] - zero_zero_marker[0], y_axis_marker[1] - zero_zero_marker[1])
    angle = math.atan2(y_axis_vector[1], y_axis_vector[0]) - math.pi / 2
    return angle

def rotate_point(point, angle, origin):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def shift_point(point, shift):
    return (point[0] + shift[0], point[1] + shift[1])

def scale_point(point, scale):
    return (point[0] * scale, point[1] * scale)

def match_and_transfer_markups(ifc_model, elements, markups, zero_zero_marker, scale, angle, ifc_origin):
    element_coords_list = []
    markup_coords_list = []
    adjusted_coords_list = []
    matched_elements = []

    # Shift and scale PDF markups to align with the IFC origin
    shift = (ifc_origin[0] - zero_zero_marker[0], ifc_origin[1] - zero_zero_marker[1])

    element_coords = [coords[:2] for element, coords in elements if coords]
    tree = KDTree(element_coords)

    for markup in markups:
        markup_coords, comment = markup
        shifted_markup_coords = shift_point(markup_coords, shift)
        scaled_markup_coords = scale_point(shifted_markup_coords, scale)
        rotated_markup_coords = rotate_point(scaled_markup_coords, angle, ifc_origin)
        adjusted_markup_coords = rotated_markup_coords
        
        _, idx = tree.query(adjusted_markup_coords)
        closest_element = elements[idx]

        element_coords_list.append(closest_element[1][:2])
        markup_coords_list.append(scaled_markup_coords)
        adjusted_coords_list.append(adjusted_markup_coords)
        matched_elements.append(closest_element[1][:2])
        transfer_markup_to_element(ifc_model, closest_element[0], comment)

    plot_matching_results(element_coords_list, markup_coords_list, adjusted_coords_list, matched_elements, zero_zero_marker, ifc_origin)

def transfer_markup_to_element(ifc_model, element, comment):
    pset_name = 'Pset_Test'
    prop_name = 'TestValue'
    owner_history = ifc_model.by_type("IfcOwnerHistory")[0]
    prop = ifc_model.createIfcPropertySingleValue(prop_name, None, ifc_model.create_entity("IfcText", comment), None)
    pset = next((pset for pset in ifc_model.by_type("IfcPropertySet") if pset.Name == pset_name), None)
    if not pset:
        pset = ifc_model.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, pset_name, None, [prop])
    else:
        if isinstance(pset.HasProperties, tuple):
            pset.HasProperties = list(pset.HasProperties)
        if not any(p.Name == prop_name for p in pset.HasProperties):
            pset.HasProperties.append(prop)
    if not any(rel.RelatingPropertyDefinition == pset for rel in element.IsDefinedBy):
        ifc_model.createIfcRelDefinesByProperties(ifcopenshell.guid.new(), owner_history, None, None, [element], pset)
    print(f"Property set '{pset_name}' with property '{prop_name}: {comment}' added to element {element.GlobalId}")

def plot_matching_results(element_coords, markup_coords, adjusted_coords, matched_elements, zero_zero_marker, ifc_origin):
    plt.figure(figsize=(10, 10))
    element_coords = list(set(tuple(coord) for coord in element_coords if coord))  # Remove duplicate coordinates
    if element_coords:
        element_x, element_y = zip(*element_coords)
        plt.scatter(element_x, element_y, c='blue', label='Element Centers')
    if markup_coords:
        markup_x, markup_y = zip(*markup_coords)
        plt.scatter(markup_x, markup_y, c='red', label='Scaled Markups')
    if adjusted_coords:
        adjusted_x, adjusted_y = zip(*adjusted_coords)
        plt.scatter(adjusted_x, adjusted_y, c='green', label='Adjusted Markups')
    if matched_elements:
        matched_x, matched_y = zip(*matched_elements)
        plt.scatter(matched_x, matched_y, c='purple', marker='x', label='Matched Elements')
    if zero_zero_marker:
        plt.scatter(*zero_zero_marker, c='black', label='PDF 0/0 Marker')
    if ifc_origin:
        plt.scatter(ifc_origin[0], ifc_origin[1], c='orange', label='IFC 0/0 Marker')

    plt.xlabel('X Coordinate (mm)')
    plt.ylabel('Y Coordinate (mm)')
    plt.title('Element and Markup Coordinates Matching')
    plt.legend()
    plt.grid(True)
    plt.show()

def parse_scale(scale_text):
    try:
        if ':' in scale_text:
            parts = scale_text.split(':')
            return float(parts[1]) / float(parts[0])
        else:
            return float(scale_text)
    except Exception as e:
        raise ValueError(f"Invalid scale format: {scale_text}. Error: {e}")

def main(ifc_path, pdf_path, storey_name, scale_text, output_path):
    scale = parse_scale(scale_text)
    ifc_model = read_ifc_file(ifc_path)
    pdf_document = read_pdf_file(pdf_path)
    zero_zero_marker, x_axis_marker, y_axis_marker, markups = extract_pdf_markups(pdf_document)
    if not zero_zero_marker or not x_axis_marker or not y_axis_marker:
        print("Missing one or more axis markers in PDF.")
        return
    angle = calculate_transformations(zero_zero_marker, x_axis_marker, y_axis_marker)
    elements, ifc_origin = extract_storey_elements(ifc_model, storey_name)
    match_and_transfer_markups(ifc_model, elements, markups, zero_zero_marker, scale, angle, ifc_origin)
    ifc_model.write(output_path)
    print(f"Updated IFC file saved to: {output_path}")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        layout = QVBoxLayout()
        self.ifc_path_label = QLabel('IFC File Path:')
        layout.addWidget(self.ifc_path_label)
        self.ifc_path_input = QLineEdit()
        layout.addWidget(self.ifc_path_input)
        self.ifc_path_button = QPushButton('Browse')
        self.ifc_path_button.clicked.connect(self.browse_ifc_file)
        layout.addWidget(self.ifc_path_button)
        self.pdf_path_label = QLabel('PDF File Path:')
        layout.addWidget(self.pdf_path_label)
        self.pdf_path_input = QLineEdit()
        layout.addWidget(self.pdf_path_input)
        self.pdf_path_button = QPushButton('Browse')
        self.pdf_path_button.clicked.connect(self.browse_pdf_file)
        layout.addWidget(self.pdf_path_button)
        self.storey_label = QLabel('Storey Name:')
        layout.addWidget(self.storey_label)
        self.storey_input = QLineEdit()
        layout.addWidget(self.storey_input)
        self.scale_label = QLabel('PDF Scale:')
        layout.addWidget(self.scale_label)
        self.scale_input = QLineEdit()
        layout.addWidget(self.scale_input)
        self.output_path_label = QLabel('Output IFC File Path:')
        layout.addWidget(self.output_path_label)
        self.output_path_input = QLineEdit()
        layout.addWidget(self.output_path_input)
        self.output_path_button = QPushButton('Browse')
        self.output_path_button.clicked.connect(self.browse_output_file)
        layout.addWidget(self.output_path_button)
        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run_main_function)
        layout.addWidget(self.run_button)
        self.setLayout(layout)
        self.setWindowTitle('IFC PDF Markup Transfer')

    def browse_ifc_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select IFC File", "", "IFC Files (*.ifc);;All Files (*)")
        if file_path:
            self.ifc_path_input.setText(file_path)

    def browse_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.pdf_path_input.setText(file_path)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save IFC File As", "", "IFC Files (*.ifc);;All Files (*)")
        if file_path:
            self.output_path_input.setText(file_path)

    def run_main_function(self):
        ifc_path = self.ifc_path_input.text()
        pdf_path = self.pdf_path_input.text()
        storey_name = self.storey_input.text()
        scale_text = self.scale_input.text()
        output_path = self.output_path_input.text()
        if not ifc_path or not pdf_path or not storey_name or not output_path:
            QMessageBox.warning(self, "Input Error", "Please provide all required inputs.")
            return
        try:
            main(ifc_path, pdf_path, storey_name, scale_text, output_path)
            QMessageBox.information(self, "Success", f"Updated IFC file saved to: {output_path}")
        except ValueError as ve:
            QMessageBox.critical(self, "Scale Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                self.ifc_path_input.setText(config.get('ifc_path', ''))
                self.pdf_path_input.setText(config.get('pdf_path', ''))
                self.storey_input.setText(config.get('storey_name', ''))
                self.scale_input.setText(str(config.get('scale', '1.0')))
                self.output_path_input.setText(config.get('output_path', ''))
        except FileNotFoundError:
            pass

    def save_config(self):
        config = {
            'ifc_path': self.ifc_path_input.text(),
            'pdf_path': self.pdf_path_input.text(),
            'storey_name': self.storey_input.text(),
            'scale': self.scale_input.text(),
            'output_path': self.output_path_input.text()
        }
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def closeEvent(self, event):
        self.save_config()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
