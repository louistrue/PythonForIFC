# IFCColorChanger

## Overview
`IFCColorChanger` is a Python-based tool designed to easily modify the color of materials in an IFC file. Utilizing a user-friendly PyQt5 interface, this tool reads a JSON file for color mapping and applies these changes to the selected IFC file.

## Features
- **Load IFC Files**: Open and view materials in any IFC file.
- **Color Mapping**: Use a JSON file to map new colors to materials.
- **Interactive GUI**: A simple and intuitive PyQt5 graphical interface.
- **Real-time Updates**: Instantly view changes and adjust as needed.
- **Save Functionality**: Export the modified IFC file with updated color schemes.

## Installation

### Prerequisites
- Python 3.x
- PyQt5
- ifcopenshell

## Usage
To start the application, run:
```bash
python IFCColorChanger.py
```

1. **Load an IFC File**: Click on 'Load IFC File' and select your file.
2. **Load Color Mapping JSON**: Ensure your JSON file with color mappings is in the correct format and path.
3. **Apply Changes**: Select materials and apply new colors.
4. **Save the File**: Save the modified IFC file with a new name.

## JSON File Format
Your JSON file should follow this format:
```json
[
    {
        "Material": "Concrete",
        "Color": [255, 255, 255]
    },
    ...
]
```

## License
tbd

## Contact
For any queries or feedback, please contact [Louis Trümpler](mailto:louis@ltplus.com).