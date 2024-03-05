import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
import ifcopenshell
from ifcopenshell import api

class IFCMergeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merge IFC Files')
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()

        self.ifc_list_widget = QListWidget()
        self.ifc_list_widget.setSelectionMode(QListWidget.MultiSelection)
        main_layout.addWidget(self.ifc_list_widget)

        select_ifc_button = QPushButton('Select IFC Files')
        select_ifc_button.clicked.connect(self.select_ifc_files)
        main_layout.addWidget(select_ifc_button)

        self.merge_button = QPushButton('Merge IFC Files')
        self.merge_button.clicked.connect(self.prepare_merge)
        main_layout.addWidget(self.merge_button)

        self.setLayout(main_layout)

        self.ifc_files = []

    def select_ifc_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select IFC Files", "", "IFC Files (*.ifc)")
        if files:
            self.ifc_files = files  # Reset list to ensure only the latest selection is stored
            self.update_ifc_list()

    def update_ifc_list(self):
        self.ifc_list_widget.clear()
        for file_path in self.ifc_files:
            self.ifc_list_widget.addItem(QListWidgetItem(file_path))

    def prepare_merge(self):
        if self.ifc_files:
            dominant_ifc_path = self.ifc_files[0]  # Assuming the first selected file is the dominant one
            merged_ifc = self.merge_ifc_files(dominant_ifc_path, self.ifc_files)
            if merged_ifc:
                output_file_path, _ = QFileDialog.getSaveFileName(self, "Save Merged IFC File", "", "IFC Files (*.ifc)")
                if output_file_path:
                    ifcopenshell.file.write(merged_ifc, output_file_path)
                    print(f"Merged IFC saved to {output_file_path}")
            else:
                print("Merge operation failed.")
        else:
            print("No IFC files selected")

    @staticmethod
    def merge_ifc_files(dominant_ifc_path, ifc_files, copy_all_levels=True):
        # Load the dominant IFC file
        dominant_ifc = ifcopenshell.open(dominant_ifc_path)
        new_ifc_file = ifcopenshell.file(schema=dominant_ifc.schema)
        levels_mapping = {}
        project_mapping = {}

        # Helper function to copy entities, avoiding duplication for specific types
        def copy_entity(entity, target_file):
            entity_types_to_skip = {'IfcProject', 'IfcSite', 'IfcOwnerHistory'}
            if entity.is_a() not in entity_types_to_skip:
                return target_file.add(entity)

        # Explicitly copy IfcProject, IfcSite, and IfcOwnerHistory from dominant
        for entity_type in ['IfcProject', 'IfcSite', 'IfcOwnerHistory']:
            for entity in dominant_ifc.by_type(entity_type):
                new_entity = new_ifc_file.add(entity)
                project_mapping[entity.id()] = new_entity

        # Adjust copied entity relationships
        def adjust_relationships(target_file):
            for entity in target_file:
                if entity.is_a('IfcRelContainedInSpatialStructure'):
                    for related_element in entity.RelatedElements:
                        if related_element.id() in project_mapping:
                            entity.RelatedElements.remove(related_element)
                            entity.RelatedElements.append(project_mapping[related_element.id()])
                elif entity.is_a('IfcRelAggregates'):
                    if entity.RelatingObject.id() in project_mapping:
                        entity.RelatingObject = project_mapping[entity.RelatingObject.id()]

        # Copy all entities from dominant IFC, except for specified types
        for entity in dominant_ifc:
            copy_entity(entity, new_ifc_file)

        # Handle levels based on user selection
        def handle_levels(source_ifc, target_file, levels_dict):
            for level in source_ifc.by_type('IfcBuildingStorey'):
                copied_level = copy_entity(level, target_file)
                if copied_level:  # Ensure level was copied
                    levels_dict[level.GlobalId] = copied_level

        # Copy levels from all files if selected, otherwise only from dominant
        if copy_all_levels:
            for ifc_path in ifc_files:
                handle_levels(ifcopenshell.open(ifc_path), new_ifc_file, levels_mapping)
        else:
            handle_levels(dominant_ifc, new_ifc_file, levels_mapping)

        # Merge entities from all files, adjusting containment and skipping as necessary
        for ifc_path in ifc_files:
            current_ifc = ifcopenshell.open(ifc_path)
            for entity in current_ifc:
                # Skip levels if not copying from all files and entity is a storey
                if entity.is_a('IfcBuildingStorey') and not copy_all_levels:
                    continue

                # Adjust spatial containment for IfcElement entities
                if entity.is_a('IfcElement') and entity.ContainedInStructure:
                    original_level_id = entity.ContainedInStructure[0].RelatingStructure.GlobalId
                    if original_level_id in levels_mapping:
                        new_level = levels_mapping[original_level_id]
                        # Clone entity to modify its containment
                        cloned_entity = ifcopenshell.api.run("entity.clone", new_ifc_file, entity=entity)
                        cloned_entity.ContainedInStructure[0].RelatingStructure = new_level

                # Add entity to the new file, avoiding duplicates
                copy_entity(entity, new_ifc_file)

        adjust_relationships(new_ifc_file)

        return new_ifc_file


def main():
    app = QApplication(sys.argv)
    ex = IFCMergeGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
