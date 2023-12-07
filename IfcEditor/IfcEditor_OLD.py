import sys
import ifcopenshell
import ifcopenshell.util.schema
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem, 
                            QListWidget, QLabel, QMenu, QAction, QTreeWidgetItemIterator)
from PyQt5.QtCore import Qt

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

        # Load IFC Files
        self.loadButton = QPushButton('Load IFC Files')
        self.loadButton.clicked.connect(self.loadFiles)
        layout.addWidget(self.loadButton)

        # Property Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Properties')
        layout.addWidget(self.tree)

        # Search Bar
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search properties...")
        self.searchBar.textChanged.connect(self.filterTree)
        layout.addWidget(QLabel("Search:"))
        layout.addWidget(self.searchBar)

        # Pending Changes List
        self.pendingList = QListWidget()
        layout.addWidget(QLabel("Pending Changes:"))
        layout.addWidget(self.pendingList)

        # Preview Changes
        self.previewTree = QTreeWidget()
        self.previewTree.setHeaderLabel('Preview Changes')
        self.previewTree.setSortingEnabled(True)
        self.previewTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.previewTree.customContextMenuRequested.connect(self.openContextMenu)
        layout.addWidget(QLabel("Preview Changes:"))
        layout.addWidget(self.previewTree)

        # Edit Operations
        self.editTextEdit = QLineEdit()
        self.applyButton = QPushButton('Confirm Changes')
        self.applyButton.clicked.connect(self.confirmChanges)
        layout.addWidget(self.editTextEdit)
        layout.addWidget(self.applyButton)

        # Undo/Redo Operations
        self.undoButton = QPushButton('Undo')
        self.undoButton.clicked.connect(self.undoChange)
        self.redoButton = QPushButton('Redo')
        self.redoButton.clicked.connect(self.redoChange)
        layout.addWidget(self.undoButton)
        layout.addWidget(self.redoButton)

        # Save Edited Files
        self.saveButton = QPushButton('Save Edited Files')
        self.saveButton.clicked.connect(self.saveFiles)
        layout.addWidget(self.saveButton)

        self.setLayout(layout)
        self.setWindowTitle('IFC Property Renamer')
        self.show()

    def updatePendingList(self):
        self.pendingList.clear()
        for change in self.pending_changes:
            self.pendingList.addItem(f"Change {change['property']} from {change['original_value']} to {change['new_value']}")

    def updatePreviewTree(self):
        self.previewTree.clear()
        # You can add code here to populate the previewTree based on the pending changes.
        # This would be similar to your existing buildPropertyTree() function, but would include the pending changes.

    def openContextMenu(self, position):
        contextMenu = QMenu()
        applyAction = QAction("Apply Change", self)
        revertAction = QAction("Revert Change", self)

        applyAction.triggered.connect(self.applyChanges)
        revertAction.triggered.connect(self.undoChange)

        contextMenu.addAction(applyAction)
        contextMenu.addAction(revertAction)
        contextMenu.exec_(self.previewTree.viewport().mapToGlobal(position))

    def loadFiles(self):
        options = QFileDialog.Options()
        filePaths, _ = QFileDialog.getOpenFileNames(self, "Load IFC files", "", "IFC Files (*.ifc)", options=options)
        if filePaths:
            self.ifc_files = [(fp, ifcopenshell.open(fp)) for fp in filePaths]
            self.displayProperties()

    def saveFiles(self):
        for fp, ifc_file in self.ifc_files:
            for change in self.pending_changes:
                search_text = change['search_text']
                replace_text = change['replace_text']
                # Note: You'll need to implement logic to find the entities and properties that match 'search_text'
                # For demonstration, let's assume 'entity' and 'property_name' are found
                entities = ifc_file.by_type('SomeEntityType')  # Replace 'SomeEntityType' with actual logic
                for entity in entities:
                    property_value = getattr(entity, 'SomePropertyName', None)  # Replace 'SomePropertyName' with actual logic
                    if property_value == search_text:
                        setattr(entity, 'SomePropertyName', replace_text)
            ifc_file.write(fp)

    def confirmChanges(self):
        selected_items = self.tree.selectedItems()
        new_value = self.editTextEdit.text()

        for item in selected_items:
            if item.parent() is None:  # Skip parent items
                continue
            
            entityType = item.parent().text(0)
            property_name = item.text(0)
            original_value = item.text(1)  # Assuming that the original value is in the second column

            change = {
                'entityType': entityType,
                'property': property_name,
                'original_value': original_value,
                'new_value': new_value
            }
            
            self.pending_changes.append(change)
            self.undo_stack.append(change)

        self.updatePendingList()
        self.updatePreviewTree()


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

    def displayProperties(self):
        self.tree.clear()
        
        for fp, ifc_file in self.ifc_files:
            for entity in ifc_file:
                if entity.is_a("IfcPropertySet"):
                    parent = QTreeWidgetItem(self.tree)
                    parent.setText(0, entity.is_a())
                    
                    for prop in entity.HasProperties:
                        child = QTreeWidgetItem(parent)
                        child.setText(0, prop.Name)
                        if prop.is_a("IfcPropertySingleValue"):
                            child.setText(1, str(prop.NominalValue.wrappedValue))



    def undoChange(self):
        if self.undo_stack:
            last_change = self.undo_stack.pop()
            self.redo_stack.append(last_change)
            self.pending_changes.remove(last_change)
            self.updatePendingList()
            self.updatePreviewTree()

    def redoChange(self):
        if self.redo_stack:
            last_undone = self.redo_stack.pop()
            self.undo_stack.append(last_undone)
            self.pending_changes.append(last_undone)
            self.updatePendingList()
            self.updatePreviewTree()


    # method for search and replace in the UI
    def searchAndReplace(self):
        search_text = self.searchBar.text()
        replace_text = self.editTextEdit.text()
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.parent():
                if search_text in item.text(0):
                    new_text = item.text(0).replace(search_text, replace_text)
                    item.setText(0, new_text)
                    # Logic to add this change to pending changes could go here
            iterator += 1

    # method to apply changes to IFC files
    def applyChanges(self):
        # Loop through the pending changes and apply them to the respective IFC files
        for change in self.pending_changes:
            entityType = change['entityType']
            property_name = change['property']
            new_value = change['new_value']
            for fp, ifc_file in self.ifc_files:
                entities = ifc_file.by_type(entityType)
                for entity in entities:
                    setattr(entity, property_name, new_value)
        # Save the modified IFC files
        for fp, ifc_file in self.ifc_files:
            ifc_file.write(fp)
        self.pending_changes.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.updatePendingList()
        self.updatePreviewTree()

# Main program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
