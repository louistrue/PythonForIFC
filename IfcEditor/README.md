# IFC File Editor Documentation

## Introduction

The IFC File Editor is a PyQt5-based application designed to allow users to load, view, and edit properties of entities in IFC files. It supports features like search, undo/redo, type validation, and a preview of pending changes.

## User Guide

### Installation

- Ensure Python and PyQt5 are installed.
- Install the `ifcopenshell` library.
- Run the application script.

### User Interface

1. **Search Bar**: Allows you to filter properties by entering text.
  
2. **Load IFC Files Button**: Opens a file dialog to load one or multiple IFC files.

3. **Save Edited Files Button**: Saves the edited IFC files.

4. **Undo/Redo Buttons**: Allows undoing or redoing changes.

5. **Properties Tree**: Displays properties of loaded IFC entities ('IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey').

6. **Edit Text Box**: Input new values for selected properties.

7. **Confirm Changes Button**: Confirms the entered change.

8. **Pending Changes List**: Lists all pending changes.

9. **Preview Changes Tree**: Displays a preview of what the properties will look like after pending changes are applied. Pending changes are shown in red.

### How to Use

1. Load IFC files by clicking "Load IFC Files".
  
2. Select a property from the Properties Tree.

3. Enter a new value in the Edit Text Box and click "Confirm Changes".

4. View pending changes in the Pending Changes List and the Preview Changes Tree.

5. Undo or redo changes using the Undo/Redo buttons.

6. Save changes by clicking "Save Edited Files".

### Features

- **Type Validation**: When confirming a change, the application validates the new value based on the expected data type of the property, using IfcOpenShell's schema utility.

## Developer Guide

### Structure

The application is built as a single `App` class inheriting from `QWidget`. It encapsulates all UI components and functionalities.

### Key Methods

- `initUI()`: Initializes the UI components.
  
- `loadFiles()`: Handles IFC file loading.

- `displayProperties()`: Populates the Properties Tree.

- `confirmChanges()`: Validates and confirms a change using IfcOpenShell for type validation.

- `filterTree()`: Filters the Properties Tree based on the search query.

- `undoChange()`, `redoChange()`: Handle undo/redo functionality.

- `updatePendingList()`: Updates the Pending Changes List.

- `updatePreviewTree()`: Updates the Preview Changes Tree.

### Libraries Used

- PyQt5: For the UI.
- ifcopenshell: For IFC file handling and schema validation for type checks.
