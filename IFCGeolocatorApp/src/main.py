import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QWidget, QAction
from PyQt5.QtCore import QUrl
from src.ui_main import MainWindow
from src.ifc_handler import IFCHandler
from src.map_viewer import MapViewer

class IFCGeolocatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainWindow()
        self.ui.setupUi(self)

        # Initialize IFC Handler and Map Viewer
        self.ifc_handler = IFCHandler()
        self.map_viewer = MapViewer(self.ui.map_viewer)
        self.ui.main_layout.addWidget(self.map_viewer)

        # Initialize coordinates for zooming
        self.site_coords = None
        self.map_conversion_coords = None

        # Set up menu actions
        self.create_actions()
        self.create_menus()

        # Connect signals and slots
        self.ui.tab_widget.currentChanged.connect(self.display_ifc_info)

        # Make cards clickable
        self.ui.site_info_group.mouseReleaseEvent = self.on_site_info_clicked
        self.ui.map_conversion_info_group.mouseReleaseEvent = self.on_map_conversion_info_clicked

    def create_actions(self):
        # Create actions for the File menu
        self.load_action = QAction("Load IFC Files", self)
        self.load_action.triggered.connect(self.load_ifc_files)

        self.export_action = QAction("Export to PDF", self)
        self.export_action.triggered.connect(self.export_to_pdf)

    def create_menus(self):
        # Create the menubar and add the File menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_action)

    def load_ifc_files(self):
        print("Load IFC Files clicked")
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open IFC Files", "", "IFC Files (*.ifc);;All Files (*)", options=options)
        print(f"Files selected: {file_paths}")
        if file_paths:
            for file_path in file_paths:
                ifc_file = self.ifc_handler.load_ifc_file(file_path)
                if ifc_file:
                    tab_content = QWidget()
                    layout = QVBoxLayout(tab_content)
                    file_label = QLabel(file_path, tab_content)
                    layout.addWidget(file_label)
                    self.ui.tab_widget.addTab(tab_content, os.path.basename(file_path))

            # Automatically select and display the first file
            self.ui.tab_widget.setCurrentIndex(0)
            self.display_ifc_info()

    def export_to_pdf(self):
        print("Export to PDF clicked")
        # Implement PDF export functionality here
        # For now, just show a message or print a log
        print("PDF export functionality is not implemented yet.")

    def display_ifc_info(self):
        print("Displaying IFC info")
        current_index = self.ui.tab_widget.currentIndex()
        if current_index != -1:
            tab = self.ui.tab_widget.widget(current_index)
            file_path = tab.layout().itemAt(0).widget().text()
            print(f"Selected file: {file_path}")
            ifc_file = self.ifc_handler.ifc_files.get(file_path)
            if ifc_file:
                project_info = self.ifc_handler.get_project_info(ifc_file)
                site_info = self.ifc_handler.get_site_info(ifc_file)
                map_conversion_info = self.ifc_handler.get_map_conversion_info(ifc_file)

                print(f"Project Info: {project_info}")
                print(f"Site Info: {site_info}")
                print(f"Map Conversion Info: {map_conversion_info}")

                self.site_coords = site_info
                self.map_conversion_coords = map_conversion_info

                # Update UI with project and site info
                self.ui.site_info_label.setText(
                    f"Project Name: {project_info['name']}\n"
                    f"Reference Latitude (DMS): {site_info['ref_lat_dms']}\n"
                    f"Reference Longitude (DMS): {site_info['ref_long_dms']}\n"
                    f"Reference Latitude (Decimal Degrees): {site_info['ref_lat_decimal']}\n"
                    f"Reference Longitude (Decimal Degrees): {site_info['ref_long_decimal']}\n"
                    f"Reference Elevation: {site_info['ref_elevation']} meters\n"
                )

                if map_conversion_info:
                    self.ui.map_conversion_info_label.setText(
                        f"Eastings: {map_conversion_info['eastings']} meters\n"
                        f"Northings: {map_conversion_info['northings']} meters\n"
                        f"Orthogonal Height: {map_conversion_info['orthogonal_height']} meters\n"
                        f"X Axis Abscissa: {map_conversion_info['x_axis_abscissa']}\n"
                        f"X Axis Ordinate: {map_conversion_info['x_axis_ordinate']}\n"
                        f"Rotation: {map_conversion_info['rotation_degrees']} degrees\n"
                        f"Scale: {map_conversion_info['scale']}\n"
                    )
                else:
                    self.ui.map_conversion_info_label.setText("No map conversion data available.")

    def on_site_info_clicked(self, event):
        print("Site info clicked")
        if self.site_coords:
            print(f"Setting map view to site coordinates: {self.site_coords['ref_lat_decimal']}, {self.site_coords['ref_long_decimal']}")
            self.map_viewer.setView(self.site_coords['ref_lat_decimal'], self.site_coords['ref_long_decimal'], 18)
            self.map_viewer.clearMarkers()
            self.map_viewer.addMarker(self.site_coords['ref_lat_decimal'], self.site_coords['ref_long_decimal'], "Site Coordinates")

    def on_map_conversion_info_clicked(self, event):
        print("Map conversion info clicked")
        if self.map_conversion_coords:
            print(f"Setting map view to map conversion coordinates: {self.map_conversion_coords['eastings']}, {self.map_conversion_coords['northings']}")
            self.map_viewer.setView(self.map_conversion_coords['eastings'], self.map_conversion_coords['northings'], 18)
            self.map_viewer.clearMarkers()
            self.map_viewer.addMarker(self.map_conversion_coords['eastings'], self.map_conversion_coords['northings'], "Map Conversion Coordinates")
            self.map_viewer.addCoordinateAxes(self.map_conversion_coords['x_axis_abscissa'], self.map_conversion_coords['x_axis_ordinate'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IFCGeolocatorApp()
    window.show()
    sys.exit(app.exec_())
