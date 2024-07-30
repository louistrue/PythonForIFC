import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QAction
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
        self.map_viewer = MapViewer(self.ui.map_viewer, self.ifc_handler.api_key)
        self.ui.main_layout.addWidget(self.map_viewer)

        # Set up menu actions and initial file load
        self.create_actions()
        self.create_menus()
        self.load_ifc_files()  # Prompt for file selection on startup

        # Connect signals and slots
        self.ui.tab_widget.currentChanged.connect(self.display_ifc_info)
        self.ui.site_info_group.mouseReleaseEvent = self.on_site_info_clicked
        self.ui.map_conversion_info_group.mouseReleaseEvent = self.on_map_conversion_info_clicked

    def create_actions(self):
        self.load_action = QAction("Load IFC Files", self)
        self.load_action.triggered.connect(self.load_ifc_files)

        self.export_action = QAction("Export to PDF", self)
        self.export_action.triggered.connect(self.export_to_pdf)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_action)

    def load_ifc_files(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open IFC Files", "", "IFC Files (*.ifc);;All Files (*)", options=options)
        if file_paths:
            for file_path in file_paths:
                ifc_file = self.ifc_handler.load_ifc_file(file_path)
                if ifc_file:
                    tab_content = QWidget()
                    layout = QVBoxLayout(tab_content)
                    file_label = QLabel(file_path, tab_content)
                    layout.addWidget(file_label)
                    self.ui.tab_widget.addTab(tab_content, os.path.basename(file_path))

            self.ui.tab_widget.setCurrentIndex(0)
            self.display_ifc_info()

    def export_to_pdf(self):
        print("Export to PDF clicked")
        print("PDF export functionality is not implemented yet.")

    def display_ifc_info(self):
        current_index = self.ui.tab_widget.currentIndex()
        if current_index != -1:
            tab = self.ui.tab_widget.widget(current_index)
            file_path = tab.layout().itemAt(0).widget().text()
            ifc_file = self.ifc_handler.ifc_files.get(file_path)
            if ifc_file:
                project_info = self.ifc_handler.get_project_info(ifc_file)
                site_info = self.ifc_handler.get_site_info(ifc_file)
                map_conversion_info = self.ifc_handler.get_map_conversion_info(ifc_file)

                self.site_coords = site_info
                self.map_conversion_coords = map_conversion_info

                self.ui.site_info_label.setText(
                    f"Project Name: {project_info['name']}\n"
                    f"Reference Latitude (DMS): {site_info['ref_lat_dms']}\n"
                    f"Reference Longitude (DMS): {site_info['ref_long_dms']}\n"
                    f"Reference Latitude (Decimal Degrees): {site_info['ref_lat_decimal']}\n"
                    f"Reference Longitude (Decimal Degrees): {site_info['ref_long_decimal']}\n"
                    f"Reference Elevation: {site_info['ref_elevation']} meters\n"
                    f"largest Coordinates: {self.ifc_handler.get_largest_coordinates(ifc_file)}\n"
                )

                if map_conversion_info:
                    epsg_info = map_conversion_info.get('epsg_info', {})
                    epsg_name = epsg_info.get('name', 'N/A') if epsg_info else 'N/A'
                    self.ui.map_conversion_info_label.setText(
                        f"EPSG Code: {map_conversion_info['epsg_code']}\n"
                        f"EPSG Name: {epsg_name}\n"
                        f"Transformation Code: {map_conversion_info['transformation_code']}\n"
                        f"Eastings: {map_conversion_info['eastings']}\n"
                        f"Northings: {map_conversion_info['northings']}\n"
                        f"Orthogonal Height: {map_conversion_info['orthogonal_height']} meters\n"
                        f"X Axis Abscissa: {map_conversion_info['x_axis_abscissa']}\n"
                        f"X Axis Ordinate: {map_conversion_info['x_axis_ordinate']}\n"
                        f"Rotation: {map_conversion_info['rotation_degrees']} degrees\n"
                        f"Scale: {map_conversion_info['scale']}\n"
                    )
                else:
                    self.ui.map_conversion_info_label.setText("No map conversion data available.")

    def zoom_to_site(self):
        if self.site_coords:
            lat = self.site_coords.get('ref_lat_decimal', 0)
            long = self.site_coords.get('ref_long_decimal', 0)
            self.map_viewer.setView(lat, long, 18)

    def zoom_to_converted(self):
        if self.map_conversion_coords:
            lat = self.map_conversion_coords.get('eastings', 0)
            long = self.map_conversion_coords.get('northings', 0)
            self.map_viewer.setView(lat, long, 18)

    def zoom_to_origin(self):
        if self.map_conversion_coords:
            epsg_code = self.map_conversion_coords.get('epsg_code', 0)
            transformation_code = self.map_conversion_coords.get('transformation_code', 0)
            origin_lat, origin_long = self.map_viewer.fetch_origin_offset(epsg_code, transformation_code)
            self.map_viewer.setView(origin_lat, origin_long, 18)

    def zoom_to_all(self):
        self.map_viewer.fitBoundsToAllMarkers()

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
            eastings = self.map_conversion_coords['eastings']
            northings = self.map_conversion_coords['northings']
            rotation = self.map_conversion_coords.get('rotation_degrees', 0)
            scale = self.map_conversion_coords.get('scale', 1.0)
            epsg_code = self.map_conversion_coords['epsg_code']
            transformation_code = self.map_conversion_coords.get('transformation_code', None)
            
            # Get the largest coordinates
            largest_coords = self.ifc_handler.get_largest_coordinates(self.ifc_handler.current_file)
            
            print(f"Setting map view to map conversion coordinates: {eastings}, {northings}")

            self.map_viewer.clearMarkers()
            self.map_viewer.applyMapConversion(
                eastings, northings, rotation, scale, 
                self.site_coords['ref_lat_decimal'], self.site_coords['ref_long_decimal'], 
                epsg_code, transformation_code, largest_coords
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IFCGeolocatorApp()
    window.show()
    sys.exit(app.exec_())
