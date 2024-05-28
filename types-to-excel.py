import sys
import ifcopenshell
import ifcopenshell.util.element
import pandas as pd
import os
from collections import defaultdict
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QCheckBox, QScrollArea, QFormLayout, QLabel, QLineEdit, QHBoxLayout
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

class IFCEntitySelector(QWidget):
    def __init__(self):
        super().__init__()

        self.ifc_file = None
        self.entities_with_types = defaultdict(list)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('IFC Entity Selector')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.load_button = QPushButton('Load IFC File', self)
        self.load_button.clicked.connect(self.load_ifc_file)
        layout.addWidget(self.load_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_layout = QFormLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.property_layout = QHBoxLayout()
        self.pset_label = QLabel('Pset Name:', self)
        self.property_layout.addWidget(self.pset_label)
        self.pset_input = QLineEdit(self)
        self.property_layout.addWidget(self.pset_input)
        self.prop_label = QLabel('Property Name:', self)
        self.property_layout.addWidget(self.prop_label)
        self.prop_input = QLineEdit(self)
        self.property_layout.addWidget(self.prop_input)
        layout.addLayout(self.property_layout)

        self.export_button = QPushButton('Export to Excel', self)
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def load_ifc_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open IFC File", "", "IFC Files (*.ifc);;All Files (*)", options=options)
        if file_name:
            self.ifc_file = file_name
            model = ifcopenshell.open(self.ifc_file)
            self.collect_entities_with_types(model)
            self.populate_entity_checkboxes()

    def collect_entities_with_types(self, model):
        for entity in model:
            if not entity.is_a().endswith('Type') and hasattr(entity, 'ContainedInStructure'):
                element_type = ifcopenshell.util.element.get_type(entity)
                if element_type:
                    entity_type = entity.is_a()
                    self.entities_with_types[entity_type].append(entity)

    def populate_entity_checkboxes(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        self.checkboxes = {}
        for entity_type in sorted(self.entities_with_types.keys()):
            checkbox = QCheckBox(entity_type)
            self.scroll_layout.addRow(checkbox)
            self.checkboxes[entity_type] = checkbox
        
        self.export_button.setEnabled(True)

    def export_to_excel(self):
        selected_entity_types = [etype for etype, cb in self.checkboxes.items() if cb.isChecked()]
        if not selected_entity_types:
            return

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if save_path:
            self.process_and_export(selected_entity_types, save_path)

    def process_and_export(self, entity_types, output_file):
        model = ifcopenshell.open(self.ifc_file)
        
        type_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        property_data = defaultdict(lambda: defaultdict(set))  # Using set to store unique values
        storeys = {storey.GlobalId: storey for storey in model.by_type('IfcBuildingStorey')}
        storeys_sorted = sorted(storeys.values(), key=lambda storey: storey.Elevation)
        storey_names = [storey.Name for storey in storeys_sorted]

        pset_name = self.pset_input.text()
        prop_name = self.prop_input.text()

        for entity_type in entity_types:
            entities = self.entities_with_types[entity_type]
            for entity in entities:
                element_type = ifcopenshell.util.element.get_type(entity)
                if element_type:
                    relating_type_name = element_type.Name
                    for struct in entity.ContainedInStructure:
                        storey = struct.RelatingStructure
                        if storey.GlobalId in storeys:
                            storey_name = storeys[storey.GlobalId].Name
                            type_data[entity_type][relating_type_name][storey_name] += 1

                    # Extract the property value if pset_name and prop_name are provided
                    if pset_name and prop_name:
                        for definition in entity.IsDefinedBy:
                            if definition.is_a('IfcRelDefinesByProperties'):
                                prop_set = definition.RelatingPropertyDefinition
                                if prop_set.is_a('IfcPropertySet') and prop_set.Name == pset_name:
                                    for prop in prop_set.HasProperties:
                                        if prop.Name == prop_name:
                                            property_data[entity_type][relating_type_name].add(prop.NominalValue.wrappedValue)

        rows = []
        for entity_type in sorted(type_data.keys()):
            for type_name in sorted(type_data[entity_type].keys()):
                row = [entity_type, type_name]
                for storey_name in storey_names:
                    row.append(type_data[entity_type][type_name].get(storey_name, 0))
                if pset_name and prop_name:
                    prop_values = ', '.join(map(str, sorted(property_data[entity_type][type_name])))  # Convert set to sorted list and join
                    row.append(prop_values)
                rows.append(row)

        columns = ['Entity', 'Type'] + storey_names
        if pset_name and prop_name:
            columns.append(f'{pset_name}::{prop_name}')
        df = pd.DataFrame(rows, columns=columns)

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Type Counts', index=False)

            # Generate and save the heatmap
            plt.figure(figsize=(20, 10))
            heatmap_data = df.drop(columns=['Entity', 'Type'] + ([f'{pset_name}::{prop_name}'] if pset_name and prop_name else []))
            heatmap_data = heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
            sns.heatmap(heatmap_data.T, annot=False, cmap='coolwarm', cbar=True, linewidths=.5, linecolor='gray')
            plt.title('Heatmap of Type Occurrences per Building Storey')
            plt.xlabel('Type')
            plt.ylabel('Building Storey')
            temp_image_path = 'temp_heatmap.png'
            plt.savefig(temp_image_path, bbox_inches='tight')
            plt.close()

            # Load the workbook and insert the heatmap image
            workbook = writer.book
            worksheet = workbook.create_sheet(title='Heatmap')
            img = Image(temp_image_path)
            worksheet.add_image(img, 'A1')

        print(f'Successfully saved the data to {output_file}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = IFCEntitySelector()
    ex.show()
    sys.exit(app.exec_())
