# VirtualElementConverter

## Overview

`VirtualElementConverter` is a Python-based tool designed for converting specific IFC classes to `IfcVirtualElement`. It offers a simplified representation of complex building structures, thereby enhancing the performance of your IFC projects.

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Starting the Application](#starting-the-application)
   - [User Interface](#user-interface)
   - [Loading an IFC File](#loading-an-ifc-file)
   - [Displaying IFC Classes](#displaying-ifc-classes)
   - [Converting to IfcVirtualElement](#converting-to-ifcvirtualelement)
   - [Saving the Modified File](#saving-the-modified-file)
- [Contributing](#contributing-)
- [License](#license-)
- [Acknowledgments](#acknowledgments)

---

## Requirements

- Python 3.x
- PyQt5
- ifcopenshell

## Installation

1. Install Python 3.x, if not already installed.
2. Install required Python packages using the command: `pip install PyQt5 ifcopenshell`.

## Usage

### Starting the Application

Execute the Python script to start the application.

### User Interface

The main user interface, displayed after launching the application, contains all necessary options for the conversion process.

### Loading an IFC File

Click on "Load IFC File" to open a file dialog and select the desired IFC file.

### Displaying IFC Classes

A dropdown menu lists all available IFC classes in the loaded file. Choose the class you wish to convert into `IfcVirtualElement`.

### Converting to IfcVirtualElement

After selecting an IFC class, click the "Convert" button to begin the conversion process.

### Saving the Modified File

A "Save As" dialog will appear after conversion. Specify the location and name for the modified IFC file.

---

## Contributing 🤝

For contributions, please create a new branch and submit a Pull Request.

---

## License 📜

The licensing details for this project are to be determined (tbd).

---

## Acknowledgments 👏

Special thanks to [IfcOpenShell](https://ifcopenshell.org) for providing the essential tools and support.