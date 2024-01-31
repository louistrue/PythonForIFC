# 🏗 IFC Property Renamer

## 📖 Introduction
The IFC Property Renamer is an open-source tool designed to simplify the process of renaming properties and property sets (Psets) within Industry Foundation Classes (IFC) files. Utilizing a graphical user interface (GUI) built with PyQt5, it provides an easy way for users to load, view, and modify IFC file properties before saving the changes back to IFC format.


## 🌟 Features
- Load and display properties and Psets from IFC files.
- Rename property sets and properties within the IFC files.
- Preview changes before applying them.
- Save and load renaming configurations in JSON format.
- Export modified IFC files with the applied changes.

## 💾 Installation

To use the IFC Property Renamer, you'll need Python installed on your system along with the necessary dependencies. Here's how you can get started:

1. Clone the repository or download the source code.
2. Install the required dependencies:

```bash
pip install PyQt5 ifcopenshell
```

## 🚀 Usage

To run the application, navigate to the directory containing the script and run:

```bash
python ifc_property_renamer.py
```

1. Click the "Load IFC File" button to select and load an IFC file.
2. Browse the property sets and properties in the loaded IFC file.
3. Enter a new name for a selected property or property set and click "Rename".
4. Preview your changes in the preview window.
5. Save your changes back to an IFC file by clicking "Save New IFC File".
6. Optionally, save and load your renaming configurations with "Save Configurations" and "Load Configurations".


## 🛠 Dependencies
- Python 3
- PyQt5
- ifcopenshell

## 🤝 Contributing

Contributions to the IFC Property Renamer are welcome! Whether it's submitting bugs, requesting features, or contributing code, your help is appreciated. Please feel free to fork the repository and submit pull requests.

## ❤️ Acknowledgments
Special thanks to IfcOpenShell for their foundational tools.

## 📄 License

tbd