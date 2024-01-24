# IFCColorChanger

## Overview

`IFCColorChanger` is a Python-based tool equipped with a PyQt5 interface, designed for efficiently modifying the color of materials in IFC files. It allows users to apply color changes using a JSON file for color mapping, providing a seamless and user-friendly experience.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
- [JSON File Format](#json-file-format)
- [Customization](#customization)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## Features

- **Load IFC Files**: Facilitates opening and viewing materials in IFC files.
- **Color Mapping**: Utilizes JSON files for defining new color mappings.
- **Interactive GUI**: Employs a user-friendly and intuitive PyQt5 interface.
- **Real-time Updates**: Allows instant visualization of color changes.
- **Save Functionality**: Enables exporting the modified IFC file with updated colors.

## Installation

### Prerequisites

- Python 3.x
- PyQt5
- ifcopenshell

Install the required libraries using pip:

```bash
pip install PyQt5 ifcopenshell
```

## Usage

Run the application using the following command:

```bash
python IFCColorChanger.py
```

Follow these steps to modify colors:

1. **Load an IFC File**: Use 'Load IFC File' to open your desired IFC file.
2. **Load Color Mapping JSON**: Ensure the JSON file with color mappings is correctly formatted and accessible.
3. **Apply Changes**: Choose materials and apply new colors.
4. **Save the File**: Export the modified IFC file under a new name.

## JSON File Format

Ensure your JSON file for color mappings adheres to this structure:

```json
[
    {
        "Material": "Concrete",
        "Color": [255, 255, 255]
    },
    ...
]
```

## Customization

The application offers flexibility in terms of color choices and material selections, allowing for customized color schemes to be applied to various materials within IFC files.

## License

The licensing details for this project are to be determined (tbd).

## Contact

For inquiries or feedback, please reach out to [Louis Trümpler](mailto:louis@ltplus.com).

## Acknowledgments

Special thanks to [IfcOpenShell](https://ifcopenshell.org) for their foundational tools.