import ifcopenshell
import ifcopenshell.util.schema
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem, QListWidget, QLabel
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItemIterator
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.ifc_files = []
        self.pending_changes = []
        self.undo_stack = []
        self.redo_stack = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Search Bar
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search properties...")
        self.searchBar.textChanged.connect(self.filterTree)

        # File Operations
        self.loadButton = QPushButton('Load IFC Files')
        self.loadButton.clicked.connect(self.loadFiles)
        self.saveButton = QPushButton('Save Edited Files')
        self.saveButton.clicked.connect(self.saveFiles)

        # Undo/Redo Operations
        self.undoButton = QPushButton('Undo')
        self.undoButton.clicked.connect(self.undoChange)
        self.redoButton = QPushButton('Redo')
        self.redoButton.clicked.connect(self.redoChange)

        # Property Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Properties')

        # Pending Changes
        self.pendingList = QListWidget()

        # Preview Tree
        self.previewTree = QTreeWidget()
        self.previewTree.setHeaderLabel('Preview Changes')

        # Edit Operations
        self.editTextEdit = QLineEdit()
        self.applyButton = QPushButton('Confirm Changes')
        self.applyButton.clicked.connect(self.confirmChanges)

        layout.addWidget(QLabel("Search:"))
        layout.addWidget(self.searchBar)
        layout.addWidget(self.loadButton)
        layout.addWidget(self.saveButton)
        layout.addWidget(self.undoButton)
        layout.addWidget(self.redoButton)
        layout.addWidget(self.tree)
        layout.addWidget(self.editTextEdit)
        layout.addWidget(self.applyButton)
        layout.addWidget(self.pendingList)
        layout.addWidget(QLabel("Preview Changes:"))
        layout.addWidget(self.previewTree)

        self.setLayout(layout)
        self.setWindowTitle('IFC File Editor')
        self.show()

    def loadFiles(self):
        options = QFileDialog.Options()
        filePaths, _ = QFileDialog.getOpenFileNames(self, "Load IFC files", "", "IFC Files (*.ifc)", options=options)
        if filePaths:
            self.ifc_files = [(fp, ifcopenshell.open(fp)) for fp in filePaths]
            self.displayProperties()

    def displayProperties(self):
        self.tree.clear()
        for entityType in ['IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey', 'IfcElementType', 'IfcElement', 'IfcSpaceType', 'IfcSpace']:
            self.buildPropertyTree(entityType)
        self.updatePreviewTree()

        def buildPropertyTree(self, entityType):
            property_dict = {}
            for fp, ifc_file in self.ifc_files:
                entities = ifc_file.by_type(entityType)
                for entity in entities:
                    for attribute_name, attribute_value in entity.get_info().items():
                        if attribute_name != "id":
                            if attribute_name not in property_dict:
                                property_dict[attribute_name] = {}
                            if attribute_value not in property_dict[attribute_name]:
                                property_dict[attribute_name][attribute_value] = []
                            property_dict[attribute_name][attribute_value].append(fp)

            entityTypeNode = QTreeWidgetItem(self.tree)
            entityTypeNode.setText(0, entityType)
            
            for attribute_name, attribute_values in property_dict.items():
                parent = QTreeWidgetItem(entityTypeNode)
                parent.setText(0, attribute_name)
                for value, files in attribute_values.items():
                    child = QTreeWidgetItem(parent)
                    child.setText(0, f"{value} (Files: {', '.join(files)})")

        self.tree.expandAll()

    def confirmChanges(self):
        selected_item = self.tree.currentItem()
        if selected_item and selected_item.parent() and selected_item.parent().parent():
            selected_property = selected_item.parent().text(0)
            selected_entity = selected_item.parent().parent().text(0)
            new_value = self.editTextEdit.text()

            # Fetch the expected data type using IfcOpenShell's schema utility
            #entity_schema = ifcopenshell.util.schema.get_entity(selected_entity)
            #attribute_schema = entity_schema.get_attribute_by_name(selected_property)
            #expected_type = attribute_schema.type_of_attribute

            # Type validation
            #try:
            #    if expected_type == "IfcInteger":
            #        new_value = int(new_value)
            #    elif expected_type == "IfcBoolean":
            #        new_value = bool(new_value)
            #    elif expected_type == "IfcFloat":
            #        new_value = float(new_value)
            #    # Add more type checks as needed
            #except ValueError:
            #    print(f"Invalid input. Expected a value of type {expected_type}.")
            #    return

            change_entry = {
                'entityType': selected_entity,
                'property': selected_property,
                'original_value': selected_item.text(0).split(' ')[0],
                'new_value': new_value
            }

            self.pending_changes.append(change_entry)
            self.undo_stack.append(change_entry)
            self.redo_stack.clear()
            self.updatePendingList()
            self.updatePreviewTree()
            self.editTextEdit.clear()


    def filterTree(self):
        search_text = self.searchBar.text().lower()
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.parent():  # Only search in child items (properties)
                if search_text in item.text(0).lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            iterator += 1


    def undoChange(self):
        if self.undo_stack:
            last_change = self.undo_stack.pop()
            self.redo_stack.append(last_change)
            self.pending_changes.remove(last_change)
            self.updatePendingList()

    def redoChange(self):
        if self.redo_stack:
            last_undone = self.redo_stack.pop()
            self.undo_stack.append(last_undone)
            self.pending_changes.append(last_undone)
            self.updatePendingList()

    def updatePendingList(self):
        self.pendingList.clear()
        for change in self.pending_changes:
            self.pendingList.addItem(f"Change {change['property']} from {change['original_value']} to {change['new_value']}")

    def saveEdits(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Edits", "", "JSON Files (*.json)", options=options)
        if filePath:
            with open(filePath, 'w') as f:
                json.dump(self.pending_changes, f)

    def saveFiles(self):
        for change in self.pending_changes:
            for fp, ifc_file in self.ifc_files:
                entities = ifc_file.by_type(change['entityType'])
                for entity in entities:
                    if getattr(entity, change['property']) == change['original_value']:
                        setattr(entity, change['property'], change['new_value'])

        for fp, ifc_file in self.ifc_files:
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getSaveFileName(self, f"Save {fp}", "", "IFC Files (*.ifc)", options=options)
            if filePath:
                ifc_file.write(filePath)

        self.pending_changes.clear()
        self.pendingList.clear()


    def loadEdits(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Edits", "", "JSON Files (*.json)", options=options)
        if filePath:
            with open(filePath, 'r') as f:
                self.pending_changes = json.load(f)
            self.pendingList.clear()
            for change in self.pending_changes:
                self.pendingList.addItem(f"Change {change['property']} from {change['original_value']} to {change['new_value']}")

    def updatePreviewTree(self):
        self.previewTree.clear()
        for entityType in ['IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey']:
            self.buildPreviewTree(entityType)

    def buildPropertyTree(self, entityType):
        property_dict = {}
        for fp, ifc_file in self.ifc_files:
            entities = ifc_file.by_type(entityType)
            for entity in entities:
                for attribute_name, attribute_value in entity.get_info().items():
                    if attribute_name != "id":
                        if attribute_name not in property_dict:
                            property_dict[attribute_name] = {}
                        if attribute_value not in property_dict[attribute_name]:
                            property_dict[attribute_name][attribute_value] = []
                        property_dict[attribute_name][attribute_value].append(fp)
        
        entityTypeNode = QTreeWidgetItem(self.tree)
        entityTypeNode.setText(0, entityType)
        
        for attribute_name, attribute_values in property_dict.items():
            parent = QTreeWidgetItem(entityTypeNode)
            parent.setText(0, attribute_name)
            for value, files in attribute_values.items():
                child = QTreeWidgetItem(parent)
                child.setText(0, f"{value} (Files: {', '.join(files)})")
        
        self.tree.expandAll()

    def buildPreviewTree(self, entityType):
        property_dict = {}
        for fp, ifc_file in self.ifc_files:
            entities = ifc_file.by_type(entityType)
            for entity in entities:
                for attribute_name, attribute_value in entity.get_info().items():
                    if attribute_name != "id":
                        if attribute_name not in property_dict:
                            property_dict[attribute_name] = {}
                        if attribute_value not in property_dict[attribute_name]:
                            property_dict[attribute_name][attribute_value] = []
                        property_dict[attribute_name][attribute_value].append(fp)

        entityTypeNode = QTreeWidgetItem(self.previewTree)
        entityTypeNode.setText(0, entityType)

        red_brush = QBrush(QColor("red"))

        for attribute_name, attribute_values in property_dict.items():
            parent = QTreeWidgetItem(entityTypeNode)
            parent.setText(0, attribute_name)
            for value, files in attribute_values.items():
                child = QTreeWidgetItem(parent)
                child.setText(0, f"{value} (Files: {', '.join(files)})")

                # Check if this property-value pair is in pending changes
                for change in self.pending_changes:
                    if change['entityType'] == entityType and change['property'] == attribute_name and str(change['original_value']) == str(value):
                        child.setForeground(0, red_brush)
                        child.setText(0, f"{change['new_value']} (Files: {', '.join(files)})")
        

# Main program
app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())


