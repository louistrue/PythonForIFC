# CSV to IFC Tool 🛠️

## Table of Contents 📑
- [Overview](#overview-)
- [Features](#features-)
- [Requirements](#requirements-)
- [Installation](#installation-)
- [Usage](#usage-)
- [Code Structure](#code-structure-)
- [Troubleshooting](#troubleshooting-)
- [Contributing](#contributing-)
- [License](#license-)
- [Acknowledgments](#acknowledgments-)

---

## Overview 🌐

This Python script enables you to generate an IFC (Industry Foundation Classes) file based on a given CSV file. It's particularly useful to generate geometric representation of measurement results like "potential field measurements" among others. The tool has an in-built color-coding system to visually represent certain values, facilitating better decision-making and ultimately enabling augmented reality use cases...

---

## Features 🌟

- **CSV Import** 📤: Import your data from a CSV file.
- **IFC Generation** 🏗️: Automatically generate an IFC file with elements, including their positions and custom properties.
- **Dynamic Styling** 🎨: Apply color-coding based on custom property values.
- **File Dialogs** 📂: GUI dialogs for opening and saving files.

---

## Requirements 📋

- Python 3.x
- `ifcopenshell` package
- `tkinter` package
- `uuid` package
- `csv` package

---

## Installation 💻

1. **Install Python 3.x from [here](https://www.python.org/downloads/).**

2. **Install required Python packages:**
    ```sh
    pip install ifcopenshell tkinter uuid csv
    ```

3. **Clone the Repository:**
    ```sh
    git clone https://github.com/louistrue/01_IfcPython/tree/main/CSV2IFC
    ```

4. **Navigate to the Directory:**
    ```sh
    cd CSV2IFC
    ```

---

## Usage 🚀

1. **Run the Script:**
    ```sh
    ifc_generator.py
    ```
2. **Open File Dialog**: A file dialog will appear. Select your input CSV file.
3. **Save File Dialog**: Another dialog will appear for you to save your IFC file.
4. **Complete**: The IFC file will be generated and saved.

---

## Code Structure 🏛️

- `create_guid()`: Generates a unique identifier.
- `create_ifcaxis2placement()`: Defines local placement.
- `create_ifcextrudedareasolid()`: Creates an extruded area solid.
- `assign_color_to_element()`: Applies color based on values.
- `create_shape()`: Generates a shape representation for elements.
- `create_ifc_hierarchy()`: Sets up the IFC file's hierarchy.
- `create_and_link_containers()`: Links the building, site, and storey.
- `process_elements_from_csv()`: Populates the IFC with elements from the CSV file.
- `create_ifc()`: Initiates the creation of the IFC file.

---

## Troubleshooting 🛠️

If you face any issues, please check the log files or reach out at [support@lt.plus](mailto:support@lt.plus).

---

## Contributing 🤝

For contributions, please create a new branch and submit a Pull Request.

---

## License 📜

tbd 

---

## Acknowledgments 👏

- IfcOpenShell https://ifcopenshell.org
- Tkinter Library