# VirtualElementConverter User Guide 📘

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Launching the Application](#launching-the-application)
  - [User Interface](#user-interface)
  - [Loading an IFC File](#loading-an-ifc-file)
  - [Viewing IFC Classes](#viewing-ifc-classes)
  - [Converting to `IfcVirtualElement`](#converting-to-ifcvirtualelement)
  - [Saving the Modified File](#saving-the-modified-file)
- [Contributing](#contributing-)
- [License](#license-)
- [Acknowledgments](#acknowledgments-)

---

## Overview 🌟

`VirtualElementConverter` is a desktop application designed for professionals in the construction sector. The application specializes in manipulating Industry Foundation Classes (IFC) files, offering functionalities like:

- 📂 Loading an existing IFC file
- 📋 Viewing IFC classes along with their occurrence counts
- 🔄 Converting selected class objects to `IfcVirtualElement`
- 💾 Saving the modified IFC file

---

## Requirements 🛠

- Python 3.x installed 🐍
- PyQt5 package installed 📦
- IfcOpenShell package installed 📦

---

## Installation ⚙️

1. **Install Python Packages**: Use the following commands to install the required packages:
    ```bash
    pip install PyQt5
    pip install ifcopenshell
    ```
2. **Download the Script**: Fetch the `VirtualElementConverter.py` Python script from the repository.

---

## Usage 📝

### Launching the Application 🚀

Execute the following command in your terminal to run the script:
```bash
python VirtualElementConverter.py
```

### User Interface 🖥

Upon launch, the application presents a clean UI composed of:

- **Load IFC File Button**: For importing an IFC file
- **IFC Class List**: Lists IFC classes and their occurrences in the loaded file
- **Convert to Virtual Element Button**: For converting selected classes to `IfcVirtualElement`
- **Save As Button**: To save your modifications

![User Interface](path/to/ui_screenshot.png)

### Loading an IFC File 📂

1. Click on the `Load IFC File` button.
2. Navigate to your desired IFC file.
3. Select the file and click "Open."

### Viewing IFC Classes 📋

After a file is loaded, the IFC Class List will populate with the IFC classes present, along with their occurrence counts.

### Converting to `IfcVirtualElement` 🔄

1. Pick the IFC class to be converted from the list.
2. Hit the `Convert to Virtual Element` button.

This will transform all objects of the chosen class to `IfcVirtualElement`.

### Saving the Modified File 💾

1. Click the `Save As` button.
2. Choose your desired save location.
3. Enter a filename and click "Save."

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