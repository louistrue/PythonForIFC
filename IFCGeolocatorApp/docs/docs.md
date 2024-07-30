### Documentation Structure

1. **Overview**
2. **Getting Started**
   - Installation
   - Running the Application
3. **User Guide**
   - Loading IFC Files
   - Viewing Project and Site Information
   - Map Interactions
   - Exporting Data
4. **Developer Guide**
   - Project Structure
   - Code Overview
   - Adding New Features
   - Testing
   - Deployment
5. **API Reference**
   - IFCHandler
   - MapViewer
   - MainWindow
6. **Contributing**
   - Code Style and Standards
   - Pull Request Process
   - Reporting Issues
7. **FAQ**
8. **License**
9. **Appendix**
   - Glossary
   - References and Further Reading

### Detailed Documentation Content

#### 1. Overview

**IFC Geolocator** is a desktop application built using PyQt5 that allows users to visualize and explore geolocation data within IFC files. It provides an interactive map view, detailed project and site information, and export capabilities.

#### 2. Getting Started

**Installation**

1. **Prerequisites**:

   - Python 3.7 or higher
   - `pip` for managing Python packages

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/IFCGeolocator.git
   cd IFCGeolocator
   ```

3. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

**Running the Application**

To start the application, navigate to the `src/` directory and run:

```bash
python main.py
```

#### 3. User Guide

**Loading IFC Files**

- Click the "Load IFC Files" button.
- Select one or more IFC files from the file dialog.
- The selected files will be listed in the sidebar.

**Viewing Project and Site Information**

- Click on an IFC file in the sidebar.
- The information panel will display details such as Project Name, Description, Site Name, and geolocation data.

**Map Interactions**

- The map displays markers for Site Location and Map Conversion Location (if available).
- Click markers for more details.
- Use the map controls to zoom and pan.

**Exporting Data**

- Click "Export to PDF" to save the displayed data and map view as a PDF document.

#### 4. Developer Guide

**Project Structure**

- `src/`: Contains the main application code.
  - `main.py`: Main entry point of the application.
  - `ui_main.py`: User interface layout and setup.
  - `ifc_handler.py`: Logic for handling IFC files.
  - `map_viewer.py`: Map visualization using Leaflet.js in QWebEngineView.
- `resources/`: Contains icons, stylesheets, and HTML templates.
- `tests/`: Unit and integration tests.
- `docs/`: Documentation and guides.

**Code Overview**

- **IFCHandler**: Responsible for loading IFC files, extracting project and site information, and handling map conversions.
- **MapViewer**: Manages the map view, adds markers, and updates the map based on IFC data.
- **MainWindow**: Sets up the main user interface, integrates UI components, and handles user interactions.

**Adding New Features**

1. **Identify the component** where the new feature will fit.
2. **Extend the functionality** in the respective file.
3. **Update the UI** in `ui_main.py` if necessary.
4. **Write tests** in the `tests/` directory to cover the new feature.

**Testing**

- Use `pytest` to run the tests located in the `tests/` directory.
- Test coverage includes unit tests for individual components and integration tests for end-to-end functionality.

**Deployment**

- The application can be packaged using tools like `PyInstaller` or `cx_Freeze`.
- Ensure all dependencies are included and the application runs smoothly on the target platform.

#### 5. API Reference

**IFCHandler**

- **load_ifc_file(file_path)**
  - Loads an IFC file and stores it in the handler.
- **get_project_info(ifc_file)**
  - Extracts and returns project-related information.
- **get_site_info(ifc_file)**
  - Extracts and returns site-related information.
- **get_map_conversion_info(ifc_file)**
  - Retrieves map conversion data if available.

**MapViewer**

- **loadMap(latitude, longitude, zoom)**
  - Loads the map centered on the specified coordinates.
- **addMarker(latitude, longitude, label)**
  - Adds a marker to the map.
- **setView(latitude, longitude, zoom)**
  - Sets the map view to the specified coordinates.
- **addCoordinateAxes()**
  - Adds X and Y axes to the map for orientation.

**MainWindow**

- **setupUi(parent)**
  - Initializes the UI elements and connects signals.
- **load_ifc_files()**
  - Handles loading of IFC files via file dialog.
- **display_ifc_info()**
  - Displays detailed information for the selected IFC file.

#### 6. Contributing

**Code Style and Standards**

- Follow PEP 8 guidelines for Python code.
- Ensure consistent use of docstrings and comments.

**Pull Request Process**

- Fork the repository and create a new branch for your feature or bugfix.
- Make your changes and ensure they are well-documented.
- Submit a pull request with a detailed description of your changes.

**Reporting Issues**

- Use the GitHub Issues page to report bugs or request new features.
- Provide as much detail as possible, including steps to reproduce the issue.

#### 7. FAQ

**Q: What is an IFC file?**

A: IFC (Industry Foundation Classes) is a standardized file format used in building and construction industries to facilitate interoperability.

**Q: Why do I see 'N/A' in some fields?**

A: 'N/A' indicates that the data is not available or not applicable for the selected IFC file.

**Q: How can I contribute to this project?**

A: Contributions are welcome! See the Contributing section above for more details.

#### 8. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

#### 9. Appendix

**Glossary**

- **IFC**: Industry Foundation Classes, a standard for data exchange in the building industry.
- **QWebEngineView**: A Qt widget that integrates web content, used here for displaying Leaflet.js maps.

**References and Further Reading**

- [IFC Overview and Specifications](https://technical.buildingsmart.org/standards/ifc/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
