# CSV to IFC Tool README

## Overview
The CSV to IFC Tool is a Python-based utility designed to convert CSV files into IFC (Industry Foundation Classes) format. This tool is especially useful for generating geometric representations of data like potential field measurements, and is equipped with a color-coding system for visual representation, enhancing decision-making and enabling augmented reality applications.

## Features
- **CSV Import**: Import data from CSV files.
- **IFC Generation**: Automatically create IFC files with detailed element positions and custom properties.
- **Dynamic Styling**: Color-code elements based on specific property values.
- **File Dialogs**: Graphical user interface dialogs for file operations.

## Requirements
- Python 3.x
- `ifcopenshell`
- `tkinter`
- `uuid`
- `csv`

## Installation
1. Install Python 3.x from the official [Python website](https://www.python.org/downloads/).
2. Install required packages: `pip install ifcopenshell tkinter uuid csv`
3. Clone the repository: `git clone https://github.com/louistrue/01_IfcPython/tree/main/CSV2IFC`
4. Navigate to the directory: `cd CSV2IFC`

## Usage
1. Run the script: `ifc_generator.py`
2. Select a CSV file through the Open File Dialog.
3. Save the generated IFC file using the Save File Dialog.

## Code Structure
- `create_guid()`: Generates unique identifiers.
- `create_ifcaxis2placement()`: Defines local placements.
- `create_ifcextrudedareasolid()`: Creates extruded area solids.
- `assign_color_to_element()`: Applies color to elements based on values.
- `create_shape()`: Generates shape representations.
- `create_ifc_hierarchy()`: Establishes IFC file hierarchy.
- `create_and_link_containers()`: Links building, site, and storey.
- `process_elements_from_csv()`: Reads elements from CSV and populates IFC.
- `create_ifc()`: Begins IFC file creation.

## Troubleshooting
For issues, consult the log files or contact [support@lt.plus](mailto:support@lt.plus).

## Contributing
To contribute, create a new branch and submit a pull request.

## License
This project's license is to be determined.

## Acknowledgments
Special thanks to IfcOpenShell (https://ifcopenshell.org).