# IFC Geolocator

IFC Geolocator is a PyQt5-based application that provides geolocation and map visualization capabilities for IFC (Industry Foundation Classes) files. The application allows users to load multiple IFC files, view detailed project and site information, and visualize the data on a map using Leaflet.js.

![User Interface](IFCGeolocatorApp/docs/IfcGeo.gif)

## Features

- **Load and Visualize IFC Files**: Load multiple IFC files and display project details and geolocation data.
- **Interactive Map**: Visualize site locations and map conversion coordinates on an interactive map.
- **Export Capabilities**: Export geolocation data and map visualizations to PDF might get added in future.
- **Modern UI**: Clean and modern user interface built with PyQt5.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Directory Structure](#directory-structure)
- [Development](#development)
- [License](#license)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.7+
- PyQt5
- ifcopenshell
- pytest (for testing)

### Clone the Repository

```bash
git clone https://github.com/yourusername/IFCGeolocator.git
cd IFCGeolocator
```

### Install Dependencies

Use pip to install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

To start the IFC Geolocator application:

```bash
python src/main.py
```

### Loading IFC Files

1. Click the "Load IFC Files" button to open a file dialog.
2. Select one or more IFC files and click "Open".
3. The selected files will be displayed in the sidebar. Click on a file to view its details and geolocation on the map.

### Exporting Data

To export the current view and data to PDF, click the "Export to PDF" button.

## Testing

### Running Tests

To run the tests, use pytest:

```bash
pytest tests/
```

Ensure you have all the test dependencies installed and configured correctly.

## Directory Structure

```
IFCGeolocatorApp/
│
├── src/
│   ├── __init__.py
│   ├── main.py               # Main entry point of the application
│   ├── ui_main.py            # UI design and layout
│   ├── ifc_handler.py        # Handling IFC file operations
│   ├── map_viewer.py         # Integration with QWebEngineView and Leaflet.js
│   ├── resources.qrc         # Resource file for images and icons
│
├── resources/
│   ├── icons/                # Icons for UI elements
│   └── templates/            # HTML templates for map display
│       └── map_template.html # HTML template with Leaflet.js
│
├── docs/                     # Documentation and guides
├── tests/                    # Unit tests for different components
│   ├── __init__.py
│   ├── test_ifc_handler.py
│   ├── test_ui.py
│   ├── test_map_viewer.py
│   ├── test_integration.py
│   └── test_data/
│       └── sample.ifc        # Sample IFC file for testing
│
├── requirements.txt          # Dependencies for the project
└── README.md                 # Project description and setup instructions
```

## Development

### Setting Up the Development Environment

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the development dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## License

This project is licensed under the AGPL3 License - see the License file in root for details.

## Contributing

Contributions are welcome!

### Issues

If you find a bug or have a feature request, please create an issue on the [GitHub Issues page](https://github.com/louistrue/pythonforifc/issues).

### Pull Requests

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

---

Thank you for using IFC Geolocator! If you have any questions or feedback, please feel free to contact us or contribute to the project.
